# SPDX-License-Identifier:Apache-2.0
# Copyright 2026 Mike Mol
"""Name queries: ask about one IDENTIFIER, across the corpus.

⚑ THE CUT RUNS WITH THE DEPENDENCY ARROW, AND THE FIRST TWO CANDIDATES RAN
AGAINST IT.  The obvious cuts were `_dispatch` (531 lines) and `_selftest` (615)
— the two biggest defs.  Both FAILED a measurement: each CONSUMES this layer
(`--calls scan` alone shows 15 call sites in the entry file, from both), while
`pycodemod` must keep re-exporting the layer for external importers and must
keep `_selftest` on itself for `run_selftests.py` to discover.  Moving a consumer
out therefore creates an import CYCLE, resolvable only by rewriting ~40 bare
calls into deferred-import lookups inside the 123 selftest cases — a large
mechanical edit through the exact code that must not lose a case.

Moving the SUPPLIER out instead makes this a leaf: it imports the core and
nothing else, and both big consumers keep calling it by plain name.  Same lines
relocated, no cycle, no edit inside the cases.  **The seam is the arrow, not the
line count** — cutting at the biggest def would have been cutting across it.

⚑ WHAT UNIFIES THESE MODES IS THE SHAPE OF THE QUESTION.  Every one takes an
IDENTIFIER and reports where it appears: `--calls`, `--dead`, `--forwards`,
`--asserted`, `--binding`, `--source`, `--attr`, `--key`, `--rivals`,
`--discards`, `--shape`.  The censuses that went to `_pycodemod_census` take no
operand and answer about the tree.  That is a difference in the question's arity,
which is a more stable boundary than topic.

⚑ `_Scan` COMES WITH THEM, AND IT IS THE REASON THIS IS ONE MODULE.  Four modes
share the visitor — the shared machinery IS the seam, not an incidental import.
Its ⚑ blocks record two false-positive classes that would each have silenced a
query rather than failing it: a def's own name is a BINDING not a reference, and
a call's own `func` name is not a value-reference — either one uncorrected makes
`--dead` report nothing as dead.  It also carries the receiver field that lets
`--calls store.connect` distinguish an aliased receiver from a resolved one.

⚑ THE `if cst is not None:` GUARD IS PRESERVED VERBATIM around `_Scan`.  This
tool stays importable with libcst absent (`--available` and the usage banner
still answer); defining a class against a `None` module would turn that into an
ImportError at load and break every consumer.
"""
import ast
import functools
import inspect
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    import libcst as cst
    import libcst.metadata  # noqa: F401
except ImportError:  # pragma: no cover - environment probe
    cst = None

import _pycodemod_core
import _pycodemod_core
# ⚑ ONE EDGE INTO THE CENSUS LAYER, AND IT IS A UTILITY NOT A CENSUS.
# `shape_sites` restricts a regex to CODE lines (excluding comments/docstrings),
# which is what `_code_lines` computes.  It sits in the census module because
# `--size` is its other consumer; it is a line classifier, not a corpus query,
# so importing it here does not make this module depend on the tree-wide layer.
from _pycodemod_census import _code_lines
# ⚑ THE ALIAS CENSUS IS BORROWED, NOT REBUILT — `alias_hint` needs to know which files
# import a module under an alias, which `aliases` already answers as the ban-compliance
# census. A second import-form parser here would be a shared NAME without a shared
# authority, the `agda_files()`-in-four-bodies shape this whole tool exists to prevent.
from _pycodemod_census import aliases as _census_aliases
# ⚑ THE DEF-CACHE TRIO FOLLOWS `_cached_defs`, ITS ONLY CONSUMER.  `_DERIVER` is
# a hash of the deriver's own source, so a change to the extraction logic
# invalidates every cached entry — the memo and the thing it keys on must stay
# reachable from one another or the invalidation silently stops working.  They
# sit in the census module for now because `--state` measures them there; this
# import is the seam correction, recorded rather than hidden.
from _pycodemod_census import _DERIVER, _PARSE_CACHE, _SCHEMA, _ignore_cache

# ⚑ `_bare_calls`'s MEMO, AND IT WAS ALMOST LEFT BEHIND — caught by exercising
# `--discards`, not by reading.  It is spelled `_BARE_CACHE: dict = {}`, an
# ANNOTATED assign, and `--layout`'s labeller only understood a plain `Assign`,
# so the census printed it as an unnamed `-` group and it was invisible in the
# move plan.  A census that cannot NAME a thing cannot be used to move it; the
# labeller has since been taught `AnnAssign` so the next reader sees the name.
_BARE_CACHE: dict = {}

#: `resorts`' PRODUCER census, keyed by the resolved population. The span query joins walked
#: files against a whole-corpus `reifies` walk; without this the walk runs once per call, and
#: TWO call sites were enough to stop it finishing (measured 2026-08-19). Same shape and same
#: reason as `_BARE_CACHE` above — one expensive derivation, many consumers.
_PRODUCER_CACHE: dict = {}




if cst is not None:
    class _Scan(cst.CSTVisitor):
        """Collect defs and call sites, structurally."""

        METADATA_DEPENDENCIES = (cst.metadata.PositionProvider,)

        def __init__(self, target=None):
            self.target = target
            self.calls = []
            self.defs = []
            self.refs = []     # (name, line) where a def's NAME is used as a VALUE
            self.kwargs = {}   # line -> set of keyword names passed at that call
            self.kwshape = {}  # line -> {keyword -> "literal" | "computed"}
            # ⚑ line -> {keyword -> the constant, or UNKNOWN}.  Gathered in the
            # SAME visit as the names and the shapes for the same reason they are:
            # the node is in hand here and nowhere else, and a later text pass over
            # the call site is the grep defect this module exists to avoid.
            self.kwvalue = {}
            # ⚑ line -> {ordinal -> the constant, or UNKNOWN} for POSITIONAL args.
            # The sibling of `kwvalue`, gathered in the same visit, existing because
            # the keyword-only reading is blind to the calls that name their target
            # by POSITION — `upsert(con, "obs", rows)`, 13 sites, every row in the
            # store.  A relation named at `args[1]` is not less structural than one
            # named at `table=`; it was merely unread.
            self.posvalue = {}
            # ⚑ line -> {ordinal -> the argument's SOURCE TEXT}.  The sibling of
            # `posvalue`, gathered in the same visit, existing because `_value_of`
            # never guesses: a bare Name reads UNKNOWN, so the reading above can say
            # a call passes `"w"` at `args[1]` and cannot say WHAT it writes.
            self.possrc = {}
            # ⚑ line -> the ENCLOSING def's name.  Added because the audit `--values`
            # exists to serve asks "the value, the file, and WHAT THAT CODE PATH IS
            # FOR", and a `path:line` pair answers two thirds of that — the third
            # was being recovered by opening 23 files by hand, which is the
            # reasoning-in-the-turn the standing rule forbids.  `literal_sites`
            # already carries exactly this column; this visitor simply had no
            # scope stack, which is also why `--dead` cannot tell a module-level
            # call from one inside `def main()`.
            self.kwctx = {}
            self._ctx = ["<module>"]
            # line -> the RECEIVER of an attribute call (`store` in `store.connect()`),
            # None for a bare `connect()`.  See visit_Call.
            self.recv = {}
            # ⚑⚑ line -> the ENCLOSING `if` CONDITIONS, outermost first ([] at the top
            # level of its scope).  A call's POSITION INSIDE A CONDITIONAL is a distinct
            # fact from where it is defined, and reading it as the latter is how a real
            # defect hid: `edit_snapshot.guard` — the mutation-intent gate — is called at
            # 61 sites, and at `drop_dead_renames.py:143` it sits under `if apply:`
            # (`:141`).  So the guard that exists to force an operator to STATE intent
            # runs only once intent has already been stated as apply, and the UNSTATED
            # case (the whole population the ratchet measures) is the one branch it can
            # never reach.  `--calls` reported that site as present and gave no way to
            # see it, so the census read as adopted while being structurally blind.
            #
            # ⚑ THE CONDITION IS RECORDED AS SOURCE TEXT, NOT EVALUATED, and saying so
            # is the honest move — the same stance `recv` takes.  `if apply:` and `if
            # args.apply:` are DIFFERENT keys here; this answers "written under this
            # test", never "reachable only when this is true".  A reader must not size a
            # fix from it as though it were a reachability proof.
            self.conds = {}
            self._cond = []
            # ⚑ A CALL'S OWN `func` NAME MUST NOT COUNT AS A VALUE-REFERENCE.
            # `f(1)` contains a Name node `f`; without this the ref set would be a
            # superset of the call set and `--dead` would report nothing as dead.
            self._call_func_nodes = set()
            # def/param NAME nodes — binding sites, never references (see below).
            self._binding_nodes = set()

        def _line(self, node):
            return self.get_metadata(cst.metadata.PositionProvider, node).start.line

        def visit_FunctionDef_name(self, node):
            """⚑ A DEF'S OWN NAME IS A BINDING, NOT A REFERENCE.  `def g(): ...`
            contains a Name node `g`; counting it would make every def reference
            itself, and `--dead` would report NOTHING as dead — silencing the query
            instead of fixing it.  Caught by this module's own "a def with no caller
            is reported dead" case, which regressed to `[]` on the first cut.
            libcst calls this hook with the `name` child specifically."""
            self._binding_nodes.add(node.name)

        def visit_Param_name(self, node):
            # Same reason: a parameter NAME is a binding site, not a use.
            self._binding_nodes.add(node.name)

        def visit_Name(self, node):
            """A bare Name in expression position — a USE-AS-VALUE, not a call.

            ⚑ THE FALSE POSITIVE THIS CLOSES, MEASURED.  `--dead` counted only
            syntactic call sites, so a function passed as a VALUE reported as dead:

                meter.create_observable_gauge("membudget_emit_unixtime",
                                              callbacks=[hb_cb])

            `scripts/membudget_otlp.py:131 hb_cb` and `:116 cb` — both live OTLP
            callbacks, both reported dead by `--dead` before this visitor existed.
            That is the shape the struct-tools rule calls out by name ("a `--dead`
            that cannot see callbacks passed as values"), and a false positive in a
            query you ACT on is a bug, not a caveat: acting on it deletes live code.

            The same shape covers decorator targets, registry-dict entries, `key=fn`
            sort arguments and `return inner` closures — every way a name is handed
            to something else instead of invoked here.
            """
            if node in self._call_func_nodes or node in self._binding_nodes:
                return
            if self.target is None or node.value == self.target:
                self.refs.append((node.value, self._line(node)))

        def visit_Call(self, node):
            f = node.func
            name = None
            recv = None
            if isinstance(f, cst.Name):
                name = f.value
                self._call_func_nodes.add(f)
            elif isinstance(f, cst.Attribute):
                name = f.attr.value
                # ⚑ THE RECEIVER WAS IN HAND AND THROWN AWAY, AND THAT IS THE
                # NAME-SCOPED-CENSUS DEFECT CLAUDE.md RECORDS.  Keeping only
                # `f.attr.value` collapses `sqlite3.connect` and `store.connect`
                # into one bare `connect`, so `--calls connect schema.py` answered
                # "33 call sites" over TWO unrelated functions — a selftest's
                # in-memory sqlite plus the real store resolver.  Sizing a fix from
                # that number is sizing it from a fact about the METHOD.
                # Free to record: the node is here, exactly as the keywords are.
                if isinstance(f.value, cst.Name):
                    recv = f.value.value
                elif isinstance(f.value, cst.Attribute):
                    recv = f.value.attr.value
            if name and (self.target is None or name == self.target):
                line = self._line(node)
                self.calls.append((name, line))
                self.recv[line] = recv
                # ⚑ THE ENCLOSING CONDITIONS, recorded here for exactly the reason the
                # receiver is: the stack is in hand, and recovering it later by text
                # would be the grep defect this module exists to avoid.  Copied, not
                # aliased — the stack mutates as the visit continues.
                self.conds[line] = list(self._cond)
                # ⚑ THE KEYWORDS ARE THE POINT FOR `forwards()`, AND THEY ARE FREE
                # HERE.  Recording them at visit time costs nothing (the node is in
                # hand) and is the only place the CST is available — a later text
                # pass over the same call site would be the grep defect this module
                # exists to avoid, since a keyword's NAME appears in prose too.
                self.kwargs[line] = {
                    a.keyword.value for a in node.args if a.keyword is not None
                }
                # ⚑ THE VALUE'S SHAPE, NOT ONLY THE KEYWORD'S NAME.  `forwards()`
                # answers "is this argument PASSED"; it cannot answer "is it a
                # LITERAL or a COMPUTED expression", and that distinction is what
                # separates a witness that MEASURES its population from one that
                # asserts a number.  Captured here for the same reason the
                # keywords are: the node is in hand, and a later text pass over
                # the call site is the grep defect this module exists to avoid.
                self.kwshape[line] = {
                    a.keyword.value: _pycodemod_core._shape_of(a.value)
                    for a in node.args if a.keyword is not None
                }
                # ⚑ THE VALUE ITSELF — WHICH literal, not merely THAT it is one.
                # `--asserted` reports `reset=True` and `reset=False` as one
                # undifferentiated LITERAL bucket, and the difference between them
                # is whether the call DROPS EVERY RELATION in the tenant.
                self.kwvalue[line] = {
                    a.keyword.value: _pycodemod_core._value_of(a.value)
                    for a in node.args if a.keyword is not None
                }
                # ⚑⚑⚑ THE POSITIONAL ARGUMENTS, WHICH ALL THREE READINGS ABOVE DROP
                # AT `a.keyword is not None` — and the drop is the reason the whole
                # family reported ZERO on the repo's highest-volume write surface.
                # `_schema.upsert(con, "obs", rows)` names its TARGET RELATION as
                # `args[1]`, a plain string literal, so `--values upsert table`
                # answered "0 of 13 call site(s) pass it" over the 13 calls that
                # write every row in the store.  The keyword filter is a fact about
                # THE METHOD reported as a fact about the substrate — the same shape
                # as the `--calls emit` census that missed `_emit_one`.
                #
                # ⚑⚑ AND A POSITION IS AS STRUCTURAL AS A NAME. The objection that
                # "position isn't self-describing, so this can't be derived" is what
                # I wrote into a hand-maintained PRODUCERS table minutes ago; it is
                # false. `args[1]` is exactly as recoverable from the CST as
                # `table=` is, and which position carries the relation is a property
                # of the CALLEE that the caller states once — not a per-site
                # judgement. Reifying the answer in a list is the thing the standing
                # rule forbids; deriving it is one dict comprehension.
                #
                # ⚑ INDEXED BY ORDINAL, INCLUDING THE STARS. A `*rest` or `**kw`
                # entry occupies its slot and reports UNKNOWN rather than shifting
                # every later index — a silent renumbering would make `args[1]` mean
                # a different argument at exactly the call sites that are hardest to
                # read, which is worse than the gap it fills (the `UNKNOWN`-is-never-
                # guessed rule, applied to the position instead of the value).
                self.posvalue[line] = {
                    i: _pycodemod_core._value_of(a.value)
                    for i, a in enumerate(node.args) if a.keyword is None
                }
                # ⚑⚑⚑ THE SEVENTH READING: WHAT THE AUTHOR WROTE AT EACH POSITION,
                # which is the one question `posvalue` STRUCTURALLY CANNOT answer.
                # `_value_of` returns UNKNOWN for every bare Name by design (it never
                # guesses a value), so a write-mode open reads `{0: UNKNOWN, 1: 'w'}` —
                # the mode is recovered and the TARGET IS NOT.  A consumer asking
                # *which variable does this call write* therefore had the CST in hand
                # and still had to recover the identifier from source text, which is
                # the grep defect this module exists to avoid, one argument over.
                #
                # ⚑ IT IS `_src_of`, THE SAME RENDERER `conds` ALREADY USES, not a
                # second spelling.  A condition test and a positional argument are
                # both "a node whose TEXT is the fact"; `visit_If` established that
                # reading and this is its sibling, so the two cannot drift apart in
                # how they render, truncate, or refuse.
                #
                # ⚑ SOURCE TEXT IS NOT A RESOLVED REFERENCE, and the honest scope is
                # the one `recv` states: this answers "spelled this way", never
                # "binds to this object".  A bare `p` and a `self.p` spelling are
                # DIFFERENT keys here, which is correct for a locator (it must point
                # at what is written) and wrong for an alias analysis (which this is
                # not, and does not claim to be).
                self.possrc[line] = {
                    i: _pycodemod_core._src_of(a.value)
                    for i, a in enumerate(node.args) if a.keyword is None
                }
                self.kwctx[line] = self._ctx[-1]

        def visit_FunctionDef(self, node):
            if self.target is None or node.name.value == self.target:
                self.defs.append((node.name.value, self._line(node)))
                # ⚑⚑ A DECORATED DEF IS REGISTERED BY ITS DECORATOR, and that
                # registration is the CALLER the census could not see.  `@test` /
                # `def S1_…()` hands the function to `test()`, which appends it to
                # a table a later loop invokes — so the def's OWN name never
                # appears as a value anywhere and `visit_Name` has nothing to
                # record.  Measured 2026-08-18: `--dead scratch/verify_shadows.py`
                # named 64 live conformance checks, the whole suite, every one
                # reachable only through `@test`.
                #
                # ⚑ THE DECORATOR IS RECORDED AS A REF ON THE DECORATED NAME, not
                # on the decorator's.  `visit_Name` already sees `test` itself (it
                # is a bare Name in decorator position); what was missing is the
                # edge in the other direction — that `S1_…` is REACHED.  Without
                # it the two names disagree: the decorator reads live and every
                # function it registers reads dead.
                #
                # A bare `@d`, a called `@d(...)` and a dotted `@a.b` all register;
                # the distinction between them is the decorator's business, not
                # the reachability question's.
                if node.decorators:
                    self.refs.append((node.name.value, self._line(node)))
            self._ctx.append(node.name.value)

        def leave_FunctionDef(self, node):
            # ⚑ THE POP MUST BE UNCONDITIONAL, and the push above is too.  Gating
            # either on `self.target` would unbalance the stack the moment a
            # name-scoped query walked a file — the enclosing context of every
            # later call in that module would then be whatever def happened to
            # match, which is a wrong answer rather than a missing one.
            self._ctx.pop()

        def visit_If(self, node):
            """Push the `if`'s TEST, as source text, onto the condition stack.

            ⚑ THE `orelse` BRANCH IS DELIBERATELY NOT NEGATED-AND-PUSHED.  libcst
            hangs `else`/`elif` off the `If` node, so a call in the `else` body is
            visited while this test is on the stack and would be reported as guarded
            BY a condition it runs when the test is FALSE — an inverted answer, which
            is worse than a coarse one.  This mode's question is "which calls sit
            under a test at all", and over-reporting the else-branch is the
            conservative direction for it: a consumer asking *is this guard behind
            `if apply:`* must still open the site.  Recorded rather than silently
            approximated, per the module's stance that a query states what it cannot
            resolve (`--values`' UNKNOWN, `--dead`'s non-static caveat).
            """
            self._cond.append(_pycodemod_core._src_of(node.test))

        def leave_If(self, node):
            # Unconditional, for the same reason `leave_FunctionDef`'s pop is: an
            # unbalanced stack answers WRONG for every later call in the module.
            if self._cond:
                self._cond.pop()
else:  # pragma: no cover
    _Scan = object


def sqlnames(name=None, paths=None):
    """[(path, line, qname, kind)] — a NAMED QUERY's definition and its call sites.

    ⚑⚑ THE BLIND SPOT THIS CLOSES IS IN A SHARED AUTHORITY, NOT A CONVENIENCE.
    The store's queries are DEFINED as `def q_<name>(…)` and INVOKED as a string
    literal — `QB.run(con, "obs_core", core_id=…)`.  The two spellings never
    meet, so `--calls q_obs_core` reports **1 def, 0 calls, ⚑ DEAD CAPABILITY**
    on a query `scripts/sppf_db.py:1023` runs every time it folds a core.

    ⚑ SO EVERY REGISTERED QUERY IS A FALSE POSITIVE IN `--dead`, and `--dead` is
    what this repo uses to find code that was built and never wired (the
    `rewire_only` class).  A census that reports live capabilities as dead is
    worse than one that misses them: it invites deletion.  MEASURED 2026-08-18 by
    a dispatched survey, which could only locate the `core_fp_mtimes` call site
    via `--binding stale` — i.e. by accident, through a neighbouring name.

    ⚑ THE `q_` PREFIX IS THE BRIDGE, AND IT IS READ FROM THE DEFINITION SIDE, not
    assumed of the string.  A def named `q_obs_core` claims the query name
    `obs_core`; a string argument matching that name is a call site.  Passing a
    name with or without the prefix both work, because an operator arriving from
    a traceback has the string and one arriving from the source has the def.
    """
    want = name[2:] if name and name.startswith("q_") else name
    rows = []
    population = list(paths or _pycodemod_core.py_files())
    # ⚑⚑ THE SAME ACCOUNTING `scan()` CARRIES, AND FOR THE SAME REASON.  This function had
    # three unaccounted swallows (unreadable / unparseable / visit-failed) — the exact
    # shape that, in `scan()`, turned a broken visitor into `0 def, 0 call, 0 ref` across
    # the whole corpus with no warning.  `sqlnames` is the bridge that stops a REGISTERED
    # QUERY reading as a DEAD CAPABILITY, so a silent zero here restores precisely the
    # false-dead verdict it exists to prevent — and `--dead` is what this repo deletes on.
    # Reported on the FUNCTION OBJECT, per-call, matching `scan.skipped`.
    sqlnames.skipped = []
    sqlnames.population = len(population)
    for p in population:
        try:
            src = open(p, encoding="utf-8").read()
        except OSError as e:
            sqlnames.skipped.append((p, "unreadable", type(e).__name__))
            continue
        # the prefilter tests the BARE query name, which appears in both
        # spellings (`q_obs_core` contains `obs_core`), so neither side is lost.
        if want and want not in src:
            continue
        try:
            _st = os.stat(p)
            _key = (p, _st.st_mtime_ns, _st.st_size)
            wrapper = _WRAPPER_CACHE.get(_key)
            if wrapper is None:
                wrapper = cst.metadata.MetadataWrapper(cst.parse_module(src))
                _WRAPPER_CACHE[_key] = wrapper
                while len(_WRAPPER_CACHE) > _WRAPPER_CACHE_MAX:
                    _WRAPPER_CACHE.popitem(last=False)
            else:
                _WRAPPER_CACHE.move_to_end(_key)
        except Exception as e:
            sqlnames.skipped.append((p, "unparseable", type(e).__name__))
            continue
        v = _SqlNameScan(want)
        try:
            wrapper.visit(v)
        except Exception as e:
            # ⚑ VISIT-FAILED IS THE TOTAL ONE: an unreadable file is a property of THAT
            # file, but a visitor defect empties EVERY file while each skip looks routine.
            sqlnames.skipped.append((p, "visit-failed", type(e).__name__))
            continue
        rows += [(p, l, q, k) for l, q, k in v.hits]
    return sorted(rows)


if cst is not None:
  class _SqlNameScan(cst.CSTVisitor):
    """Collect `def q_<name>` definitions and string-literal query references.

    ⚑ A STRING ARGUMENT IS NOT A CALL, and conflating them would re-introduce the
    defect one level down.  `QB.run(con, "obs_core")` REFERENCES the query; the
    CALL is to `run`.  The row kind says which, so a reader is never told a
    string literal was invoked.

    ⚑⚑⚑ THE `if cst is not None` GUARD WAS MISSING HERE AND PRESENT ON `_Scan`, so the
    module's OWN ImportError fallback (`cst = None`, line 51) was DEFEATED BY ONE CLASS.
    A base-class expression evaluates at IMPORT, so `class _SqlNameScan(cst.CSTVisitor)`
    raised `AttributeError: 'NoneType' object has no attribute 'CSTVisitor'` before any
    guard could run — turning a graceful degradation into a hard crash for every caller
    without `libcst`, including modes that need no CST at all.

    ⚑⚑ MEASURED BY THREE PARTIES IN ONE AFTERNOON, and I was the last to see it.
    `friction-borrowed-tool-needs-its-owners-interpreter` (mikemol-github-io) was already
    on summit's floor naming this tool; cassian-observability hit the identical
    `AttributeError` adopting it; and summit-c4 reproduced it INSIDE THE CAPABILITY CHECK
    I HAD JUST WRITTEN TO GATE THIS FILE — a check that passes under my interpreter and
    fails under theirs.  **The record catching the report is the same act that exposed
    the record repeating it.**  The reports were not merely unread, they were unapplied.
    """
    METADATA_DEPENDENCIES = (cst.metadata.PositionProvider,)

    def __init__(self, want):
        self.want = want
        self.hits = []

    def _line(self, node):
        return self.get_metadata(cst.metadata.PositionProvider, node).start.line

    def visit_FunctionDef(self, node):
        nm = node.name.value
        if nm.startswith("q_") and (self.want is None or nm[2:] == self.want):
            self.hits.append((self._line(node), nm[2:], "def"))

    def visit_SimpleString(self, node):
        # ⚑ THE RAW VALUE, STRIPPED OF ITS QUOTES — `node.value` includes them,
        # so a naive compare never matches and the mode would report zero
        # references while looking like it ran.
        try:
            val = node.evaluated_value
        except Exception:
            return
        if not isinstance(val, str) or not val:
            return
        if self.want is None:
            # unscoped: only strings that look like a registered query name,
            # otherwise every literal in the corpus is a "hit"
            return
        if val == self.want:
            self.hits.append((self._line(node), val, "ref"))


def scan(paths=None, target=None, kwseen=None):
    """[(path, kind, name, line)] — defs and calls across the corpus.

    ⚑ `kwseen` IS AN OPT-IN, CONTEXT-STAMPED ACCUMULATOR — see `KwIndex`.  Pass one
    and it is filled with `(path, line) -> {keyword names passed at that call}` AND
    stamped with the query that produced it, so a later read under a different
    query RAISES rather than answering from the wrong population.  The row list
    keeps its shape, so no existing caller moves.

    ⚑ THE `rewire_only` CLASS: a def with no call anywhere is a capability that was
    built and never wired.  `grep` answers this badly — it cannot distinguish a
    call from a mention in a docstring or a ⚑ comment, and these files are DENSE
    with both (a grep for a tool's own name here returns mostly prose; the audit
    that found `rewire_only` had to read the one hit to see it was the definition).
    The CST knows the difference by construction.

    ⚑ A CHEAP PREFILTER, BECAUSE POSITION METADATA IS THE EXPENSIVE PART.
    `MetadataWrapper` resolves a position for EVERY node in the file; over an
    85-file corpus of 2000-line tools that exceeded a 120s budget even scoped to
    `scratch/`.  But a file that does not contain the target's TEXT at all cannot
    contain a call to it, so a substring test skips almost every file for a
    single-name query.  The text scan only ever ADDS candidates — the CST still
    decides — so this cannot reintroduce the grep defect it is layered over
    (a docstring mention passes the prefilter and is then correctly rejected).
    """
    # ⚑ A DOTTED TARGET SELECTS BY RECEIVER, and it is the fix for the name-scoped
    # census CLAUDE.md records ("a --calls <name> census is NAME-SCOPED, NOT
    # CAPABILITY-SCOPED").  `--calls connect schema.py` reported 33 sites over two
    # unrelated functions (a selftest's `sqlite3.connect` and the real
    # `store.connect`), and a fix sized from that number is sized from the method.
    # `store.connect` now answers only the latter; the bare spelling is unchanged,
    # so no existing caller moves.
    #
    # ⚑ THE RECEIVER IS SYNTACTIC, NOT RESOLVED, and saying so is the honest move:
    # this matches the TEXT of the receiver, so an aliased import (`import store as
    # _store`) is a DIFFERENT key.  That is why the prefilter below tests the bare
    # name — an alias must still be findable — and why a dotted query answers
    # "spelled this way", never "resolves to this module".
    recv_want = None
    if target and "." in target:
        recv_want, target = target.rsplit(".", 1)
    rows = []
    population = list(paths or _pycodemod_core.py_files())
    # ⚑⚑⚑ A FILE THIS SCAN COULD NOT READ IS NOT A FILE WITH NOTHING IN IT, and until
    # 2026-08-18 nothing here could tell those apart.  A `NameError` in the visitor
    # (mine, adding `visit_If`) was swallowed by the `except Exception: continue` below,
    # and EVERY `--calls` query in the corpus began answering `0 def, 0 call, 0 ref` —
    # a clean zero, no warning.  `--dead` read GREEN on a file with 18 defs, because
    # zero rows means zero unreachable rows, and `--dead` is what this repo DELETES on.
    #
    # ⚑⚑ THE SWALLOW IS LOAD-BEARING AND STAYS: one unparseable file must not abort a
    # corpus query.  The DEFECT was never the skip — it was that the skip was INVISIBLE,
    # so the population silently shrank and no number said so.  `scan.skipped` is that
    # number; consumers report `n of m` (SKILL.md:274 — a bare list cannot distinguish
    # "no matches" from "no file read").
    #
    # ⚑ RESET PER CALL, on the function object itself, because `scan()` is memoised at
    # several call sites and a module-level accumulator would report a PREVIOUS query's
    # skips against this one — the stale-population defect `KwIndex`'s stamp exists to
    # prevent, reintroduced through the accounting meant to close it.
    scan.skipped = []
    scan.population = len(population)
    if kwseen is not None:
        # ⚑ STAMP AT THE POINT OF GATHERING — the only place the context is known.
        # Stamping in the caller would restore exactly the unchecked precondition
        # this class exists to remove.
        kwseen.target = target
        kwseen.population = frozenset(population)
    for p in population:
        try:
            src = open(p, encoding="utf-8").read()
        except OSError as e:
            scan.skipped.append((p, "unreadable", type(e).__name__))
            continue
        # ⚑ NOT a skip: a file that does not contain the target's TEXT cannot contain a
        # call to it, so this exclusion is SOUND and belongs to the query, not to
        # failure.  Counting it as skipped would cry wolf on every named query — which
        # is the fastest way to get a real skip ignored.
        if target and target not in src:
            continue
        # ⚑⚑⚑ THE PARSE IS CACHED ACROSS CALLS, and the measurement is why. `pipeflow`
        # asks five whole-corpus questions per graph build (`consumers`, `producers`,
        # `callgraph`, two `values`), each memoised so each runs ONCE — and the build
        # still took 331s, of which `--profile` attributed **330s to 227 `scan()`
        # calls**. Nothing was redundant at the caller level; the corpus was simply
        # PARSED FIVE TIMES. I hoisted four memos by guessing before measuring, and the
        # guesses were wrong: the cost was never a repeated call, it was the parse.
        #
        # ⚑⚑ AND `target=None` DEFEATS THE PREFILTER THIS DOCSTRING RELIES ON. The
        # substring test skips almost every file for a NAMED query, which is what keeps
        # `--calls` fast — but `callgraph` scans for every name, so every file parses.
        # The prefilter is not wrong; it simply cannot apply to the whole-corpus question,
        # and that question is the one a dataflow trace needs.
        #
        # ⚑ KEYED ON (path, mtime, size) SO A STALE TREE IS IMPOSSIBLE. A bare path key
        # would serve a pre-edit CST to a post-edit query — the silent-wrong-answer class
        # this file's `KwIndex` stamp exists to prevent, reintroduced through a cache.
        try:
            _st = os.stat(p)
            _key = (p, _st.st_mtime_ns, _st.st_size)
            wrapper = _WRAPPER_CACHE.get(_key)
            if wrapper is None:
                wrapper = cst.metadata.MetadataWrapper(cst.parse_module(src))
                _WRAPPER_CACHE[_key] = wrapper
                while len(_WRAPPER_CACHE) > _WRAPPER_CACHE_MAX:
                    _WRAPPER_CACHE.popitem(last=False)
            else:
                _WRAPPER_CACHE.move_to_end(_key)
        except Exception as e:
            scan.skipped.append((p, "unparseable", type(e).__name__))
            continue
        v = _Scan(target)
        try:
            wrapper.visit(v)
        except Exception as e:
            # ⚑⚑ THIS IS THE ONE THAT HID A BROKEN VISITOR, and it is the most dangerous
            # of the three because it fails for EVERY file at once.  An unreadable or
            # unparseable file is a property of that file; a visitor defect is a property
            # of the QUERY, so it empties the whole corpus while each individual skip
            # looks routine.  A caller seeing `skipped == population` is looking at a
            # broken scan, not a clean tree — which is why the count travels with the
            # rows rather than being logged and forgotten.
            scan.skipped.append((p, "visit-failed", type(e).__name__))
            continue
        if recv_want is not None:
            # a receiver-qualified query asks about CALL SITES; a def carries no
            # receiver, so folding defs in would answer a different question.
            _hits = [(n, l) for n, l in v.calls if v.recv.get(l) == recv_want]
            rows += [(p, "call", n, l) for n, l in _hits]
            # ⚑⚑⚑ THE `kwseen` FILL BELOW WAS UNREACHABLE FOR A DOTTED TARGET, and the
            # failure mode was a SILENT EMPTY INDEX — the exact class `KwIndex`'s
            # context stamp exists to prevent, arriving through the one path the stamp
            # cannot see.  A caller passing `kwseen` with `os.replace` got a correctly
            # stamped index containing NOTHING, so every reading (`possrc`, `positions`,
            # `contexts`, `conds`) answered "absent" rather than raising.  Measured:
            # `check_snapshot_guard` read `possrc[0]` for `shutil.rmtree(self._tmp)` as
            # `None` and therefore could not tell a self-owned tempdir teardown from a
            # destruction of the caller's content.
            #
            # ⚑ THE STAMP GUARDS THE POPULATION, NOT THE FILL.  `.check()` compares
            # target and paths, both of which were correct here — the index was
            # legitimately gathered for this query and simply never written to.  An
            # empty-but-valid index is indistinguishable from "the query found nothing",
            # which is why this is a wrong answer rather than an error.
            if kwseen is not None:
                _lines = {l for _n, l in _hits}
                for l in _lines:
                    if l in v.kwargs:
                        kwseen[(p, l)] = v.kwargs[l]
                    if l in v.kwshape:
                        kwseen.shapes[(p, l)] = v.kwshape[l]
                    if l in v.kwvalue:
                        kwseen.constants[(p, l)] = v.kwvalue[l]
                    if l in v.kwctx:
                        kwseen.contexts[(p, l)] = v.kwctx[l]
                    if l in v.posvalue:
                        kwseen.positions[(p, l)] = v.posvalue[l]
                    if l in v.possrc:
                        kwseen.possrc[(p, l)] = v.possrc[l]
                    if l in v.recv:
                        kwseen.receivers[(p, l)] = v.recv[l]
                    if l in v.conds:
                        kwseen.conds[(p, l)] = v.conds[l]
            continue
        rows += [(p, "def", n, l) for n, l in v.defs]
        rows += [(p, "call", n, l) for n, l in v.calls]
        # ⚑ A THIRD KIND, NOT A WIDENED `call`.  A use-as-value is genuinely not a
        # call — `--calls` answers "where is this INVOKED" and folding refs into it
        # would corrupt that answer (and `--forwards`, which reads keywords off call
        # nodes that a ref does not have).  `dead()` consults both kinds; every other
        # consumer filters on kind and is therefore unmoved.
        rows += [(p, "ref", n, l) for n, l in v.refs]
        if kwseen is not None:
            kwseen.update({(p, l): ks for l, ks in v.kwargs.items()})
            # ⚑ SHAPES RIDE THE SAME CONTEXT-STAMPED CARRIER.  A second bare dict
            # would reintroduce exactly the unchecked-precondition defect
            # `KwIndex` exists to close — the caller would have to REMEMBER which
            # scan filled it.  Stamped once, checked once, read together.
            for l, sh in v.kwshape.items():
                kwseen.shapes[(p, l)] = sh
            # ⚑ THE VALUES RIDE THE SAME STAMPED CARRIER, for the third time and
            # for the same reason: a second bare dict would put the provenance
            # back in the caller's memory, which is the unchecked precondition
            # `KwIndex` exists to remove.
            for l, vals in v.kwvalue.items():
                kwseen.constants[(p, l)] = vals
            for l, ctx in v.kwctx.items():
                kwseen.contexts[(p, l)] = ctx
            # ⚑ THE POSITIONS RIDE IT TOO — fifth reading, one scan, one stamp.
            for l, pv in v.posvalue.items():
                kwseen.positions[(p, l)] = pv
            # ⚑ AND THE POSITIONAL SOURCE TEXT — seventh reading, one scan, one stamp.
            for l, ps in v.possrc.items():
                kwseen.possrc[(p, l)] = ps
            # ⚑ AND THE RECEIVER — eighth reading, already computed by the visitor for
            # its own dotted-target filter and previously discarded at the boundary.
            for l, rv in v.recv.items():
                kwseen.receivers[(p, l)] = rv
            # ⚑ AND THE ENCLOSING CONDITIONS — sixth reading, same scan, same stamp.
            # The five above are facts about a call's ARGUMENTS; this is a fact about
            # where the call SITS, which is the axis that hid `guard` behind `if apply:`.
            for l, cs in v.conds.items():
                kwseen.conds[(p, l)] = cs
    return rows


def swallows(paths=None):
    """[(path, line, kind, handler)] — every `except` that DISCARDS the exception.

    ⚑⚑⚑ THE SHAPE THAT MADE A BROKEN SCANNER READ AS A CLEAN TREE.  On 2026-08-18 a
    `NameError` in `_Scan.visit_If` was swallowed by `scan()`'s per-file
    `except Exception: continue`, and EVERY `--calls` query in the corpus returned
    `0 def, 0 call, 0 ref` — no warning, no exit code.  `--dead`, the census this repo
    DELETES on, read GREEN on a file with 18 defs, because zero rows means zero
    unreachable rows.

    ⚑⚑ THE SWALLOW IS USUALLY CORRECT AND MUST NOT BE DELETED — one unparseable file
    must not abort a corpus query.  What is never correct is a swallow that leaves NO
    TRACE: the population silently shrinks and no number says so.  So this reports the
    POPULATION, not a verdict — a `continue`/`pass` handler is a site that owes an
    accounting, and whether it has one is the reader's call.

    ⚑ `continue` AND `pass` ARE STATEMENTS, SO `--calls`/`--guarded` CANNOT SEE THEM.
    That is why this exists rather than a filter over an existing mode: the census asked
    `--guarded continue` and got `0 of 0`, which is a fact about the METHOD (a call-site
    reader cannot see a statement) presented as a fact about the code.  Measured, then
    built.

    `kind` distinguishes what is discarded:
      bare-except   `except:`               — also swallows KeyboardInterrupt/SystemExit
      broad         `except Exception:`     — every programming error in the block
      narrow        `except OSError:` etc.  — a stated, expected failure
    and `handler` is `continue` | `pass` | `return` — the three silent exits.
    """
    rows = []
    for p in list(paths or _pycodemod_core.py_files()):
        try:
            src = open(p, encoding="utf-8").read()
        except OSError:
            continue
        try:
            tree = ast.parse(src)
        except SyntaxError:
            continue
        for node in ast.walk(tree):
            if not isinstance(node, ast.ExceptHandler):
                continue
            # a handler that only continues/passes/returns bare is a DISCARD; one that
            # logs, re-raises, or returns a value is an accounting and not this census.
            body = [s for s in node.body if not isinstance(s, ast.Expr)
                    or not isinstance(s.value, ast.Constant)]   # drop a docstring
            if len(body) != 1:
                continue
            s = body[0]
            if isinstance(s, ast.Continue):
                h = "continue"
            elif isinstance(s, ast.Pass):
                h = "pass"
            elif isinstance(s, ast.Return) and s.value is None:
                h = "return"
            else:
                continue
            if node.type is None:
                kind = "bare-except"
            elif isinstance(node.type, ast.Name):
                kind = "broad" if node.type.id in ("Exception", "BaseException") \
                    else "narrow"
            else:
                kind = "narrow"
            rows.append((p, node.lineno, kind, h, _feeds_verdict(tree, node)))
    return sorted(rows)


def _feeds_verdict(tree, handler):
    """Does the swallowed work FEED A COUNTED RESULT, or only produce output?

    ⚑⚑⚑ THE DISCRIMINATOR, AND IT CAME FROM TWO SITES IN ONE FILE.  `reuse_check.py`
    interns a reference corpus in a loop and swallows a failure at `:68` — but the
    corpus SIZE is a verdict input, so a file that silently fails to intern makes
    `reuse_check` report *"no prior art"* as a fact about the SUBSTRATE.  Eleven lines
    later, `:71` performs the SAME call on the proposal and exits with the reason.
    **Same file, same operation, two policies** — which is the evidence that the split
    is real and not a taste judgement.

    ⚑⚑ THE CONTRAST CASE IS EQUALLY STRUCTURAL.  `wg_profile.py:305` wraps a block whose
    only effect is `print` — if it fails a diagnostic is missing and no verdict moves.
    Benign, and it must not be reported beside the corpus-truncating one, or the census
    becomes a list nobody triages.

    So: a handler FEEDS A VERDICT when its `try` body mutates a name that outlives the
    block — an append/add/update to an accumulator, or an assignment to a name the
    enclosing function returns.  It does NOT when the body only calls `print`/`log`.

    ⚑ CONSERVATIVE BY CONSTRUCTION, AND THE DIRECTION IS DELIBERATE.  An unresolvable
    body reports `feeds` (report a benign site, not miss a corpus-truncating one) — the
    same asymmetry `--guarded` takes on the `else` branch: over-report, never invert.
    This is a TRIAGE ORDER, not a verdict; every row still needs the site opened.
    """
    out_only = True
    touched = set()
    # the `try` this handler belongs to: located by identity, since ast gives no parent
    owner = None
    for node in ast.walk(tree):
        if isinstance(node, ast.Try) and handler in node.handlers:
            owner = node
            break
    if owner is None:
        return True                            # cannot resolve → report (conservative)
    for s in (x for st in owner.body for x in ast.walk(st)):
        if isinstance(s, ast.Call):
            f = s.func
            nm = f.attr if isinstance(f, ast.Attribute) else \
                (f.id if isinstance(f, ast.Name) else "")
            if nm in ("append", "add", "update", "extend", "setdefault", "insert"):
                return True                    # an accumulator grew inside the try
            # ⚑⚑ A METHOD CALL MUTATES ITS RECEIVER, AND MISSING THAT FAILED THE OTHER
            # CONTROL CASE.  My second cut tracked only ASSIGNED names, so
            # `reuse_check.py:68` — `(C.add_agdai if … else C.add_file)(f)` — read as
            # `output`: nothing is assigned in that try, the corpus grows INSIDE the
            # method, and `:70` then reads `len(C.units)` as the verdict input.  Two cuts,
            # each failing one control case in the opposite direction, is what forced the
            # receiver into the model rather than a third guess.
            # ⚑ WALK THE WHOLE `func`, NOT JUST A TOP-LEVEL `Attribute`.  The control case
            # spells its callee as a CONDITIONAL EXPRESSION —
            # `(C.add_agdai if f.endswith(".agdai") else C.add_file)(f)` — so `func` is an
            # `IfExp` and a top-level `isinstance(f, ast.Attribute)` test sees nothing.
            # The receiver is real either way; only the spelling moved.
            for a in ast.walk(f):
                if isinstance(a, ast.Attribute):
                    for r in ast.walk(a.value):
                        if isinstance(r, ast.Name):
                            touched.add(r.id)
            if nm not in ("print",) and not nm.startswith(("log", "warn", "debug")):
                out_only = False
        if isinstance(s, (ast.Assign, ast.AugAssign, ast.AnnAssign)):
            out_only = False
            for t in ast.walk(s):
                if isinstance(t, ast.Name):
                    touched.add(t.id)
    if out_only:
        return False                           # only printed — a missing diagnostic
    # ⚑⚑ THE TEST IS "READ AFTER THE BLOCK", NOT "ASSIGNED INSIDE IT" — and the coarser
    # version FAILED ITS OWN CONTROL CASE.  My first cut called any assignment
    # verdict-feeding, so `wg_profile.py:305` (a KNOWN-BENIGN print block that assigns
    # `_rows = _sc.stats()` and consumes it in the very next loop) came back VERDICT.
    # It classified 5 of 5 as VERDICT — a discriminator that discriminates nothing, and
    # exactly the flattering direction: a triage order where everything is urgent is a
    # flat list wearing a ranking.  A name ASSIGNED and then CONSUMED inside the try is
    # local scaffolding; only a name still READ downstream can carry a silent drop out.
    if owner_scope := next(
            (n for n in ast.walk(tree)
             if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef, ast.Module))
             and owner in list(ast.walk(n))), None):
        # ⚑ WALK THE ORIGINAL STATEMENTS, not a synthetic `ast.Module` wrapper: `id()`
        # identity is the whole mechanism here, and re-wrapping would give fresh nodes
        # that match nothing — the set would be empty and every name would read as
        # "outside", restoring the always-VERDICT bug one level down.
        inside = {id(x) for s in owner.body for x in ast.walk(s)}
        # ⚑⚑ DOWNSTREAM ONLY — A READ *BEFORE* THE TRY IS AN INPUT, NOT AN ESCAPE, AND
        # MISSING THAT MADE 46 OF 50 READ VERDICT.  `buildtime.py:35-44` builds `row`
        # at `:37-39`, then writes it inside the try; `row` lands in `touched` (it is a
        # Name in the call) and is read at `:37` — ABOVE the block. A bare membership
        # test called that an escape, so a plainly benign best-effort append reported
        # VERDICT. The escape question is strictly "is this still read AFTER the try",
        # so compare positions rather than mere membership.
        #
        # ⚑ AND THE ISOLATED FIXTURE DID NOT REPRODUCE IT — my probe passed `row` as a
        # PARAMETER and reported `False` correctly, while the live site reported `True`.
        # A case pinned to a fixture that is not shaped like the corpus tests the fixture.
        end = max((getattr(x, "lineno", 0) for s in owner.body
                   for x in ast.walk(s)), default=owner.lineno)
        for r in ast.walk(owner_scope):
            if isinstance(r, ast.Name) and isinstance(r.ctx, ast.Load) \
                    and r.id in touched and id(r) not in inside \
                    and getattr(r, "lineno", 0) > end:
                return True                    # read AFTER the try → escapes
        return False
    return True                                # unresolved → conservative


def guarded(name, paths=None):
    """([(path,line,conds)] calls UNDER an `if`, [(path,line)] calls at the top level).

    ⚑⚑⚑ THE AXIS `--calls` COULD NOT SEE, AND IT HID A REAL DEFECT IN A GATE.  Every
    other reading in this module answers a question about a call's ARGUMENTS — was the
    keyword passed, was it literal, which constant, which position.  None answers where
    the call SITS, and that is where `edit_snapshot.guard` went wrong: it is called at
    61 sites, and at `drop_dead_renames.py:143` it sits inside `if apply:` (`:141`).

    ⚑⚑ SO THE MUTATION-INTENT GATE RUNS ONLY AFTER INTENT IS STATED.  `guard` exists to
    force an operator to say `--apply` or `--dry-run` rather than defaulting; placed
    under `if apply:`, it is reached only once apply has been chosen.  **The unstated
    case — the entire population the ratchet was built to measure — is the one branch it
    can never reach.**  It is a WRITE guard where a DECISION guard was specified, and no
    paydown fixes that: a default-dry run never reaches the guard, so the census reads
    clean forever.  `--calls` reported the site as present and gave no way to see it.

    ⚑ THE CONDITION IS SOURCE TEXT, NOT AN EVALUATION, and this answers "written under
    this test" — never "reachable only when this is true".  `if apply:` and
    `if args.apply:` are DIFFERENT keys.  A reader must not size a fix from this as
    though it were a reachability proof; it is the same stance `recv` takes (a receiver
    is matched syntactically, so an aliased import is a different key).

    ⚑ THE `else` BRANCH IS OVER-REPORTED, DELIBERATELY.  libcst hangs `else`/`elif` off
    the `If` node, so a call in the else-body is visited with the test still on the
    stack.  Negating and pushing it would report that call as guarded BY a condition
    that is FALSE there — an INVERTED answer, which is worse than a coarse one.  Both
    sides are returned so a bare list of guarded calls can never read as the whole
    population, the same reason `forwards()` reports what is missing AND what is not.
    """
    population = list(paths or _pycodemod_core.py_files())
    seen = KwIndex()
    rows = [r for r in scan(population, name, kwseen=seen) if r[1] == "call"]
    # read through the context check, not around it — see `forwards()`
    seen.check(name, population)
    under, top = [], []
    for p, _k, _n, line in rows:
        cs = seen.conds.get((p, line), [])
        (under.append((p, line, cs)) if cs else top.append((p, line)))
    return sorted(under), sorted(top)


def forwards(name, kw, paths=None):
    """([(path, line)] passing `kw`, [(path, line)] NOT passing it) at calls to `name`.

    ⚑ THE QUESTION A FLAG ROLLOUT ACTUALLY ASKS, AND `--calls` COULD NOT ANSWER.
    When a capability is added to a shared AUTHORITY (`ratchet.set_ratchet` gaining
    `list_keys`, and before it `agda_files`, `edit_snapshot.guard`, `head_span`), the
    work is never "does this call the authority" — every caller does, which is what
    makes it an authority — it is **which callers have been migrated and which have
    not**.  That is a per-call-site fact about ARGUMENTS, and it was being answered
    by piping `grep -c` over a file list and reading the table by eye: two commands
    and an interpretation step, i.e. reasoning not codified.

    ⚑ AND THE TEXT ROUTE IS WRONG HERE FOR THE SAME REASON IT IS WRONG FOR `--calls`.
    `grep -c -- '--list'` counts the FLAG STRING, which appears in `check_argv` known-
    sets, in usage text, and in ⚑ comments about the flag — so it reports a gate as
    migrated when it merely mentions the migration.  The keyword at the call node is
    the fact; everything else is prose about the fact.

    Deliberately reports BOTH sides.  A bare list of what is missing reads as the
    whole population, and this arc has recorded four times that a tally without its
    denominator becomes a stale dependency.

    ⚑ NO "DECLINED" BUCKET — AND BUILDING ONE WAS THE DEFECT (user, 2026-08-01:
    *"the whole thing about 'leave the richer ones alone' is a DRY failure; they
    should all be lifted to a common thing"*).  I had four gates printing richer
    output than the authority could, concluded they must keep their own `--list`,
    and started building a MARKER so this query would stop reporting them.  That is
    machinery whose only job is to record that a duplication is intentional — the
    weak-beside-strong class (§18) with a permission slip stapled to it.  The
    difference between those four and the authority is ONE LINE (how to render a
    key); everything around it — the flag parse, the sort, the loop, the return —
    is the copy.  The lift is `render=` on `set_ratchet`, so the RENDERING varies
    and the DISPATCH does not.  MISSING therefore means missing, with no second
    category to hide in.
    """
    population = list(paths or _pycodemod_core.py_files())
    seen = KwIndex()
    rows = [r for r in scan(population, name, kwseen=seen) if r[1] == "call"]
    # ⚑ READ THROUGH THE CONTEXT CHECK, NOT AROUND IT.  This call is trivially
    # satisfied today (the same frame gathered it) — its job is to make the
    # requirement STRUCTURAL, so a future caller that threads a shared or cached
    # index in here gets an exception instead of an answer from the wrong query.
    seen.check(name, population)
    has, lacks = [], []
    for p, _k, _n, line in rows:
        (has if kw in seen.get((p, line), set()) else lacks).append((p, line))
    return sorted(has), sorted(lacks)


def _changed_files(rev, root=None):
    """(set_of_abspaths, description) of the `.py` files a change touched — or REFUSES.

    ⚑ THE CHANGE IS GIT'S FACT, NOT THIS TOOL'S, so this asks git and does not model it.
    Two spellings are accepted and they mean genuinely different things:

        WORKING   `--rev WORKING`  — the uncommitted diff against HEAD (what I am about
                  to commit). This is the shape that fired twice today: the widening was
                  in the working tree and the un-updated callers were too.
        <range>   any revision expression `git diff --name-only` accepts — `HEAD~1`,
                  `abc123..def456`, `main...topic`. A committed change, after the fact.

    ⚑⚑ THERE IS NO DEFAULT, AND THAT IS THE DESIGN. A mode that silently assumed `HEAD`
    would be GUESSING AT THE AUTHOR'S INTENT: "the callers I did not update in the same
    change" is a different question for an uncommitted edit than for the last commit, and
    picking one produces a confident answer to a question nobody asked. The refusal names
    both spellings, which is cheaper than a wrong population.
    """
    import subprocess
    root = root or _pycodemod_core.ROOT
    if rev == "WORKING":
        cmd = ["git", "diff", "--name-only", "HEAD"]
        desc = "the uncommitted working diff against HEAD"
    else:
        cmd = ["git", "diff", "--name-only", rev]
        desc = "git diff --name-only %s" % rev
    try:
        r = subprocess.run(cmd, cwd=root, capture_output=True, text=True, timeout=60)
    except (OSError, subprocess.SubprocessError) as e:
        return None, "git could not be run: %s" % e
    if r.returncode != 0:
        # ⚑ GIT'S OWN REFUSAL IS PASSED THROUGH VERBATIM. A bad revision must not be
        # normalised into "no files changed" — an empty population and an unparseable
        # revision are opposite facts, and only one of them means the change is clean.
        return None, "git refused %r: %s" % (rev, r.stderr.strip() or "(no message)")
    out = set()
    for rel in r.stdout.splitlines():
        rel = rel.strip()
        if rel.endswith(".py"):
            out.add(os.path.abspath(os.path.join(root, rel)))
    return out, desc


def fix_owes_callers(name, rev, paths=None, root=None):
    """(rows, meta) — call sites of `name` that the change did NOT also touch. Ⓝ10.

    A def changed in `rev`; every call site of it in a file `rev` did NOT touch is a
    caller that may not have been updated with it. Rows are `(path, line, kind)`; `meta`
    carries the population facts a reader needs to size the answer.

    ⚑⚑⚑ THE DEFECT, AND IT FIRED TWICE IN ONE HOUR IN THE MEMORY GENERATORS. `_load()`'s
    return tuple was widened from 2 elements to 4. `--calls _load` finds FOUR call sites;
    the author had updated three, and the fourth still unpacked a 2-tuple and would have
    raised. A second case widened a helper's signature the same way. Both were caught BY
    HAND. `--calls` knows where the callers are and `git diff` knows what the change
    touched, and nothing joined them — the join is the whole mode.

    ⚑⚑⚑ AND THIS IS A FLOOR, NOT A COUNT — SAY SO AT EVERY CALL SITE. Three independent
    reasons, and none of them is fixable here:

      1. THE CENSUS IS NAME-SCOPED, NOT CAPABILITY-SCOPED. `scan` matches the bare token,
         so a call reached through an aliased module (`import store as _s; _s.tenant(…)`)
         is a DIFFERENT key. `pycodemod`'s own banner records the measurement: `--calls
         tenant store.py` says "1 def, 0 calls, DEAD CAPABILITY" while the same name over
         its real callers says "0 def, 7 calls". Same name, same tool, opposite verdicts.
         `alias_hint` below cross-checks and the CLI prints it, but a cross-check that
         finds nothing is a fact about the METHOD.
      2. A NAME IS NOT A DEFINITION. Five unrelated `_load`s exist in this corpus, and
         this mode cannot tell them apart — `--calls _load` over the tree returns all
         five's call sites. A dotted `recv.name` target narrows by RECEIVER when the
         caller spells one; nothing narrows by which `def` a bare call resolves to.
      3. TOUCHED IS NOT UPDATED. A file the change touched is EXCLUDED, on the assumption
         that the author who edited it looked at it. That assumption is exactly what fails
         when a change edits a file for an unrelated reason — so the excluded population
         is reported as a count, never silently dropped.

    ⚑⚑ THE ASYMMETRY THAT MAKES THE FLOOR THE SAFE DIRECTION. This repo DELETES on
    `--dead`, so an under-reporting census there removes live code. Here the action a row
    invites is "go look at this call site", so a MISSED row costs a defect that ships and
    a SPURIOUS row costs a glance. Under-reporting is therefore the failure that matters,
    which is why every blind class above is printed rather than assumed away.

    ⚑ THE DEF ITSELF IS NOT A ROW. A call site inside the changed file is presumed seen;
    so is the `def` line. What is reported is strictly the un-touched callers.
    """
    root = root or _pycodemod_core.ROOT
    changed, desc = _changed_files(rev, root)
    if changed is None:
        return None, {"refused": desc}
    population = list(paths or _pycodemod_core.py_files())
    rows = scan(population, name)
    # ⚑ `call` AND `ref` BOTH COUNT — a use-as-value is a use. `dead`'s own ⚑ block
    # records the measurement: `cb` returned from a factory and `hb_cb` passed as
    # `callbacks=[hb_cb]` read as DEAD before the `ref` kind existed. A widened signature
    # breaks a `key=fn` handoff exactly as it breaks a direct call.
    uses = [(p, line, k) for p, k, _n, line in rows if k in ("call", "ref")]
    defs = [(p, line) for p, k, _n, line in rows if k == "def"]
    owed = sorted((p, line, k) for p, line, k in uses if p not in changed)
    covered = [u for u in uses if u[0] in changed]
    meta = {
        "rev": rev,
        "desc": desc,
        "changed_py": len(changed),
        "defs": len(defs),
        # ⚑ THE DEFINITION SITES THE CHANGE ACTUALLY TOUCHED. If this is ZERO the whole
        # question is malformed — the name's def was not in the change, so "callers not
        # updated with it" has no referent, and the CLI says so rather than printing an
        # alarming list of every call site in the tree.
        "defs_changed": len([p for p, _l in defs if p in changed]),
        "uses": len(uses),
        "covered": len(covered),
        "population": len(population),
        "skipped": list(getattr(scan, "skipped", ())),
        "alias_hint": alias_hint(name, defs, population),
    }
    return owed, meta


def alias_hint(name, defs, population):
    """[(file, line, alias, module)] — modules holding `name`'s def, imported UNDER AN ALIAS.

    ⚑⚑ THE CROSS-CHECK THE BANNER DEMANDS, AND IT IS A HINT BECAUSE IT CANNOT BE A PROOF.
    `--calls` is blind to `import store as _s; _s.tenant(…)`. This reports every file that
    imports one of `name`'s DEFINING modules under an alias — those are the files where a
    bare-token census is known to be blind, so a reader knows WHERE to look rather than
    being told the census was complete. It does NOT resolve the alias to a call: doing so
    would be a second name-resolver beside `scan`'s, one authority over two spellings.

    ⚑ AN EMPTY RESULT IS A FACT ABOUT THIS PROBE. It means no aliased import of a defining
    module was found in the scanned population — not that the call census is complete.
    """
    mods = {os.path.splitext(os.path.basename(str(p)))[0] for p, _l in defs}
    if not mods:
        return []
    out = []
    for f, line, form, module, bound, _scope in _census_aliases(population):
        # ⚑ ONLY THE TWO ALIASING FORMS. `BARE` and `FROM` bind the name the census can
        # already see, so they are not blind spots; `AS-MOD` (`import store as _s`) and
        # `FROM-AS` (`from store import tenant as _t`) are the two that rename, and
        # renaming is exactly what makes a bare-token probe miss the call.
        if form not in ("AS-MOD", "FROM-AS"):
            continue
        head = str(module).split(".")[0]
        # ⚑ `bound` HAS TWO SHAPES AND READING ONLY ONE WOULD MISS HALF THE POPULATION —
        # census-keyed-on-one-spelling, in the cross-check written against that class.
        # `AS-MOD` binds `[asname]`; `FROM-AS` binds `"name as alias"` strings.
        names = set()
        for b in (bound or ()):
            b = str(b)
            names.add(b.split(" as ")[0].strip())
            names.add(b.split(" as ")[-1].strip())
        if head in mods or (names & mods):
            out.append((str(f), line, ",".join(str(b) for b in (bound or ())) or str(module),
                        str(module)))
    # ⚑⚑⚑ THE NARROWING — Ⓝ19, AND IT IS A RECOVERY, NOT MERELY A FILTER. Until this, the
    # arm reported every file importing a DEFINING MODULE under an alias, whether or not
    # that file calls THIS name — so a reader was handed six files and had to run `--attr`
    # by hand on each. `attr_reads` is RECEIVER-AGNOSTIC by construction (its own docstring:
    # it matches `.name` on ANY receiver), so it catches every alias spelling rather than
    # the ones a caller thought to guess, and joining on it keeps only files that really
    # read `.name`.
    #
    # ⚑⚑ MEASURED, AND THE THIRD CASE IS THE ONE THAT MATTERS. `set_ratchet`: 6 candidate
    # files -> 0. `check_argv`: 5 -> 1, and that one the bare probe had already found. Those
    # two look like pure noise-suppression. `py_files`: 6 -> 1, and that file
    # (`_pycodemod_selftest.py`) holds THREE genuine `_core.py_files(...)` calls under a
    # FUNCTION-SCOPED `import _pycodemod_core as _core` — real blind-class-1 call sites the
    # bare-token census cannot see at all. So the join both suppresses and RECOVERS.
    #
    # ⚑ THE CALL LINES REPLACE THE IMPORT LINE, because the import line is not where the
    # reader must look. A row now names a site to open.
    #
    # ⚑ ITS OWN OVER-REPORT IS BOUNDED AND STATED AT THE SOURCE: `.name` on any receiver
    # over-reports for a COMMON name (`.value`, `.name`) and is exact for a distinctive one.
    # That residue is strictly smaller than the whole-file rows it replaces, so this cannot
    # be worse than what it narrows — but it is NOT resolution, and the floor language above
    # stays exactly as it was. A quieter output must not read as a stronger claim.
    if not out:
        return []
    # ⚑⚑ THE ROW IS KEYED ON THE CALL SITE, AND THE FIRST CUT CROSS-PRODUCTED. A file may
    # carry SEVERAL aliasing imports of the same module (`_c` at module scope, `_core`
    # inside a function), and each attribute read is ONE site regardless of how many
    # aliases are in scope. Joining the two lists directly multiplied 2 imports x 3 call
    # lines into 12 rows for 3 real sites — a count inflated 4x by the arity mismatch, in
    # the arm added to make the arm more honest. Aliases are COLLECTED per file; the site
    # is the key.
    per_file = {}
    for f, _l, alias, module in out:
        per_file.setdefault(f, (set(), set()))
        per_file[f][0].add(alias)
        per_file[f][1].add(str(module))
    narrowed = []
    for p, line, _ctx in attr_reads(name, sorted(per_file)):
        p = str(p)
        if p not in per_file:
            continue
        al, mods_seen = per_file[p]
        narrowed.append((p, line, "|".join(sorted(al)), "|".join(sorted(mods_seen))))
    return sorted(set(narrowed))


def asserted(name, kw, paths=None):
    """([(path,line)] passing a LITERAL, [(path,line)] passing a COMPUTED value).

    ⚑ THE QUESTION `--forwards` COULD NOT ANSWER, and it is about MAGNITUDE
    (user, 2026-08-03: *"why are these tooling items not manifesting any kind of
    relative importance compared to each other?"*).

    `--forwards` reports whether a caller PASSES an argument.  For a keyword whose
    job is to carry a POPULATION — `size=`, `count=`, `n=` — presence is not the
    fact; whether the value was COUNTED is.  A literal means the caller asserted a
    number; a computed expression means it measured one.

    MEASURED ON THE LIVE CASE: `items.T25_LIBRARY` returns `size=1` from a branch
    that short-circuits BEFORE reaching its predicate, and `T28_CLOSURE` returns
    `len(gaps)` over a two-branch decision tree — so both can only ever report 0
    or 1.  `size` is the LAST sort key in `(layer, grade-1, lev, size)`, so two
    items whose size cannot vary are guaranteed to tie forever.  The tie between
    them was never a missing edge; it was a missing MEASUREMENT inside each.

    ⚑ A LITERAL IS NOT AUTOMATICALLY A DEFECT, which is why this REPORTS rather
    than judges.  `size=1` is correct for a genuinely singular population — one
    module, one gap — and every `other:*` failure class emits exactly that, one
    part per module.  What the rows expose is a witness whose size CANNOT VARY
    with the thing it measures; deciding which of those is wrong is reading, not
    counting.  A predicate that called all 45 of them defects would be the
    false-positive-into-a-ratchet hazard this repo has recorded twice.
    """
    population = list(paths or _pycodemod_core.py_files())
    seen = KwIndex()
    rows = [r for r in scan(population, name, kwseen=seen) if r[1] == "call"]
    seen.check(name, population)
    lit, comp = [], []
    for p, _k, _n, line in rows:
        shape = seen.shapes.get((p, line), {}).get(kw)
        if shape == "literal":
            lit.append((p, line))
        elif shape is not None:
            comp.append((p, line))
    return sorted(lit), sorted(comp)


def values(name, kw, paths=None):
    """([(path, line, value, ctx)] for every call passing `kw`, total call sites).

    `kw` is a KEYWORD name, or an INTEGER (an ordinal) to read the positional
    argument at that index — see the ⚑ at the `_pos` binding below for why the
    ordinal is a spelling of this question rather than a second mode.

    `value` is the constant the caller wrote, or `UNKNOWN` when the argument is not
    a simple literal.  `ctx` is the ENCLOSING def (or `<module>`).  The rows are
    exactly the sites `forwards()` reports as `has`; the split by `value is UNKNOWN`
    is exactly `asserted()`'s (literal, computed).

    ⚑ `ctx` IS PART OF THE ANSWER, NOT A CONVENIENCE.  The audit this mode was built
    for asks for "the value, the file, and WHAT THAT CODE PATH IS FOR"; a `path:line`
    pair answers two thirds and leaves the third to be recovered by opening the files
    by hand — reasoning in the turn instead of in the program.

    ⚑ THE THIRD MEMBER OF A FAMILY THAT STOPPED ONE STEP SHORT, AND THE STEP IT
    STOPPED SHORT OF IS THE ONE THAT ANSWERS "IS THIS CALL DANGEROUS."  `--forwards`
    answers *which* call sites pass the keyword; `--asserted` answers *literal vs
    computed*; nothing reported the VALUE.  Measured on the live case:
    `sandbox_connect(reset=…)` has **23 call sites, all passing a literal**, and the
    toolkit could not say which of them pass `True` — while `reset=True` calls
    `store.sandbox_reset()`, which DROPS EVERY RELATION in the tenant.  So the
    repo's most destructive keyword surface was unauditable with the repo's own
    tools, and `grep` at a `.py` is hook-refused by design: a toolkit gap, not a
    category, which is exactly the distinction the standing rule is about.

    ⚑ THE DENOMINATOR IS THE CALL POPULATION, NOT THE ROW COUNT.  `n of m` where
    `m` counts every call to `name`, so a reader can tell *no site passes it* from
    *no file was read* — the failure a bare list cannot distinguish, recorded four
    times in this arc as a tally that became a stale dependency.

    ⚑ AND IT NEVER GUESSES.  An f-string with interpolation, a bare name, an
    attribute read, a conditional, a call — each reports `UNKNOWN`, which is a
    distinct row and not a dropped one.  A reader that rendered `reset=flag` as a
    value would be worse than the gap it fills: the gap is visible and the
    fabrication is not, and this particular fabrication would be read as clearance
    to run a `DROP`.  `UNKNOWN` is a sentinel rather than `None` because `None` is
    itself a literal a caller can pass.
    """
    population = list(paths or _pycodemod_core.py_files())
    seen = KwIndex()
    rows = [r for r in scan(population, name, kwseen=seen) if r[1] == "call"]
    seen.check(name, population)
    # ⚑⚑ AN ORDINAL IS A SPELLING OF THE SAME QUESTION, NOT A SECOND MODE.  `kw`
    # given as an integer (or a decimal string) selects the POSITIONAL argument at
    # that index instead of a keyword.  A sibling `positions()` function would have
    # duplicated the population walk, the stamp, the check, the UNKNOWN handling and
    # the sort — the four-gates-with-one-line-different shape this module's own
    # `--asserted` docstring records as the defect (*"they should all be lifted to a
    # common thing"*).  The ONE line that differs is which index the row is keyed by.
    # ⚑ THE PER-ROW DECISION IS `_value_at`, SHARED WITH `values_many`. It was inline
    # here and would have been copied there — one question, two bodies, which is the
    # defect this module's banner opens with (`agda_files()` as four bodies).
    out = []
    for p, _k, _n, line in rows:
        got = _value_at(seen, p, line, kw)
        if got is not _MISSING:
            out.append((p, line, got, seen.contexts.get((p, line), "<module>")))
    # ⚑ SORTED ON (path, line) ONLY.  A row's third element may be `UNKNOWN`, an
    # arbitrary object, or a mix of `bool`/`str`/`int` — sorting the whole tuple
    # would raise a TypeError on a corpus that happens to pass two kinds, i.e. a
    # crash whose trigger is the data rather than the query.
    return sorted(out, key=lambda r: (r[0], r[1])), len(rows)


def values_many(names, paths=None):
    """{name: ([(path, line, value, ctx)], total)} — several `values()` in ONE scan.

    ⚑⚑⚑ TWO WHOLE-CORPUS SCANS FOR TWO NAMES WAS THE MEASURED COST. `pipeflow` asks
    `values("upsert", 1)` and `values("run", 1)`; `--profile` attributed **149s of a 196s
    build to two `values` calls**, each walking and visiting the entire corpus for one
    name. The scan is the expensive thing, the name is a filter applied during it, and
    nothing required one scan per filter.

    ⚑⚑ AND IT IS `target=None` PLUS A POST-FILTER, NOT N SCANS IN A LOOP. A loop would
    keep the per-name traversal and only share the parse; scanning once for every call
    site and partitioning by name afterwards pays the traversal once for the whole set.
    The prefilter that makes a NAMED scan fast cannot apply here — every file may contain
    one of the names — which is exactly the trade this function exists to make explicit.

    ⚑ EACH RETURNED PAIR IS WHAT `values(name)` WOULD RETURN, including the denominator,
    so a consumer swapping to this cannot silently change an answer. The ordinal/keyword
    handling is shared rather than reimplemented: this delegates the per-row decision to
    the same `_value_at` both use.
    """
    population = list(paths or _pycodemod_core.py_files())
    seen = KwIndex()
    rows = [r for r in scan(population, None, kwseen=seen) if r[1] == "call"]
    seen.check(None, population)
    out = {}
    for want, kw in names.items():
        hits, total = [], 0
        for p, _k, nm, line in rows:
            if nm != want:
                continue
            total += 1
            got = _value_at(seen, p, line, kw)
            if got is not _MISSING:
                hits.append((p, line, got, seen.contexts.get((p, line), "<module>")))
        out[want] = (sorted(hits, key=lambda r: (r[0], r[1])), total)
    return out


_MISSING = object()


def _value_at(seen, p, line, kw):
    """The value of `kw` (keyword name or positional ordinal) at one call site.

    ⚑ ONE DECISION, TWO CALLERS. `values` and `values_many` both need "is this a keyword
    or an ordinal, and what is there" — duplicating it would be the four-gates-one-line-
    different shape this module's `--asserted` docstring records.
    """
    pos = kw if isinstance(kw, int) else (int(kw) if isinstance(kw, str)
                                          and kw.isdigit() else None)
    vals = seen.positions.get((p, line), {}) if pos is not None \
        else seen.constants.get((p, line), {})
    key = pos if pos is not None else kw
    return vals[key] if key in vals else _MISSING


def callgraph(paths=None):
    """{"module.caller" -> {callee names}} — the call graph, caller-attributed.

    ⚑⚑⚑ `--calls` COULD NOT ANSWER THIS, AND ITS OWN DOCSTRING SAYS WHY. The `_Scan`
    visitor *"records call sites with NO scope tracking, so a module-level `build_index()`
    and one inside `def main()` are indistinguishable"* — it answers WHERE a name is
    called, never WHICH FUNCTION does the calling. So "does this function reach `upsert`
    through a helper" was unanswerable, and every reachability question collapsed to
    "does the name appear in this file".

    ⚑⚑ THE CONTEXT COLUMN ALREADY EXISTED, unread for this purpose. `KwIndex.contexts`
    maps `(path, line) -> enclosing def`, built for `--values` so an audit could say
    *"the value, the file, and WHAT THAT CODE PATH IS FOR"*. A call graph is that same
    index taken over EVERY name instead of one — a scan with `target=None` — so this is a
    reading of existing machinery rather than a second traversal of the corpus.

    ⚑ CALLERS ARE MODULE-QUALIFIED, CALLEES ARE BARE, and the asymmetry is honest rather
    than sloppy: a caller is a definition site (its module is known), while a callee is a
    NAME AT A CALL SITE whose module is not resolved — `upsert` here is the spelling, not
    a resolved symbol. The same caveat `scan`'s receiver handling states: this answers
    "spelled this way", never "resolves to this definition".
    """
    out = {}
    for p in list(paths or _pycodemod_core.py_files()):
        seen = KwIndex()
        rows = [r for r in scan([p], None, kwseen=seen) if r[1] == "call"]
        seen.check(None, [p])
        mod = os.path.splitext(os.path.basename(p))[0]
        for _p, _k, name, line in rows:
            ctx = seen.contexts.get((_p, line), "<module>")
            out.setdefault("%s.%s" % (mod, ctx), set()).add(name)
    return out


def reaches(callgraph_, start, targets, depth=6):
    """The callees in `targets` reachable from `start`, with the path that got there.

    ⚑⚑ TRANSITIVE, BECAUSE THE DIRECT JOIN MISSES THE COMMON SHAPE (operator: *"You'll
    also need to trace transient dependencies through the python call graph"*). A
    function that runs a builder and writes through a HELPER has the read and the write
    in two different bodies, so a same-body join reports no round trip where there is
    one. `_do_promote` reading `unprojected_cores` and delegating the write to
    `pack_core_sql` is exactly that.

    ⚑ DEPTH-BOUNDED AND THE BOUND IS REPORTED, never silent. An unbounded walk over a
    recursive corpus does not terminate usefully, and a truncated one that says nothing
    reports "no path" for "I stopped looking" — the absent-vs-empty confusion this repo
    keeps paying for. Returns `{target: [path…]}`; a target absent from the result was
    not reached WITHIN `depth`.
    """
    # ⚑⚑⚑ A BARE CALLEE NAME IS NOT A RESOLVED SYMBOL, AND WALKING IT AS ONE MANUFACTURES
    # PATHS. The first cut expanded every callee to EVERY module-qualified caller sharing
    # that suffix, so a generic name bridged unrelated subsystems: it reported
    # `sppf_query.cmd_fanin → wg_engine.run → proofcost._emit → query_defs.verify →
    # sppf_db.build → write_events` as a dataflow path. That is `wg_engine.run`, not
    # `QB.run` — 26 of 29 reported round trips were this fabrication, and each looked
    # entirely plausible. The `--calls emit` defect CLAUDE.md records (a name-scoped census
    # read as capability-scoped), reached through a transitive closure that amplifies it.
    #
    # ⚑⚑ SO EXPANSION IS SAME-MODULE ONLY, and that is a REFUSAL rather than a heuristic:
    # a call to a name defined in this module is a hop this scanner can honestly attribute,
    # and a call to an imported name is one it cannot — the receiver is syntactic, so
    # `run` here and `run` there are the same token and different functions. Resolving
    # imports is a different instrument; claiming to have done it is the failure.
    #
    # ⚑ THE COST IS UNDER-REPORTING, WHICH IS THE SAFE DIRECTION. A genuine cross-module
    # chain now reads as "not reached", i.e. a fact about this method — the same honesty
    # the `no entry for that spelling` refusals carry. An over-report is a fabricated
    # dependency someone acts on.
    #
    # ⚑⚑ AND THE `mod.callee` KEY IS A COINCIDENCE TEST, NOT A RESOLUTION. It asks "does
    # THIS module also define a function by that name" — which is true both when the
    # module defines it and when the module IMPORTS it and the importer's own key happens
    # to exist. Measured: `sppf_db.write_events → _insert_decoded` resolves as a
    # same-module hop although `_insert_decoded` lives in `sppf_decode`; the hop is real,
    # but this walk got it by the name colliding, not by following the import. A path is
    # therefore EVIDENCE OF A CHAIN, never proof of one, and a reader chasing a specific
    # edge should confirm it at the source. Import resolution is the mode this is not.
    found, frontier, seen_fn = {}, [(start, [start])], {start}
    for _ in range(depth):
        nxt = []
        for fn, path in frontier:
            mod = fn.rsplit(".", 1)[0]
            for callee in sorted(callgraph_.get(fn, ())):
                if callee in targets and callee not in found:
                    found[callee] = path + [callee]
                cand = "%s.%s" % (mod, callee)
                if cand in callgraph_ and cand not in seen_fn:
                    seen_fn.add(cand)
                    nxt.append((cand, path + [cand]))
        if not nxt:
            break
        frontier = nxt
    return found


def verdict_returners(paths=None):
    """{name -> (path, line)} — every def whose contract is a RETURNED VERDICT.

    ⚑ DERIVED, NEVER RECALLED.  My first statement of this item listed five names
    from memory (`may_write`, `blockers`, `log_is_fresh`, `blame`, `roundtrip`) —
    the hand-drawn-population miss §69 caught, where the repo already draws the line
    and I proposed a list without looking.  A verdict-returner is DISCOVERABLE: it
    returns something a caller is meant to ACT ON rather than merely receive.

    The predicate, deliberately narrow so the census is readable (§63: *a census too
    wide to read has already failed*): a function that returns a BOOL, an EXIT CODE,
    or `None`-as-"all clear" on at least one path AND a non-`None` verdict on
    another.  A function returning data (a dict, a list of rows) is excluded — a
    caller that ignores a returned LIST has done nothing dangerous, while a caller
    that ignores a returned REFUSAL has disabled a guard.

    That asymmetry is the whole point, and it is the same one `should_keep` records
    one domain over: the cost of missing a dropped verdict is an inert guard that
    passes everything; the cost of a false row here is one line of review.
    """
    if cst is None:
        return {}
    out = {}
    for path in list(paths or _pycodemod_core.py_files()):
        try:
            src = open(path, encoding="utf-8").read()
            mod = cst.parse_module(src)
            wrapper = cst.metadata.MetadataWrapper(mod)
            pos = wrapper.resolve(cst.metadata.PositionProvider)
        except Exception:
            continue

        class V(cst.CSTVisitor):
            METADATA_DEPENDENCIES = (cst.metadata.PositionProvider,)

            def visit_FunctionDef(self, node):
                # ⚑ DO NOT DESCEND INTO `_selftest` — every def inside it is a
                # TEST-LOCAL helper (see the note below), and returning False here
                # both excludes them and skips the walk.  `_selftest` itself returns
                # a bool, but it is an entry point, not an authority anyone calls.
                if node.name.value == "_selftest":
                    return False
                vals = []

                class R(cst.CSTVisitor):
                    def visit_Return(self, r):
                        vals.append(r.value)
                    # do NOT descend into a nested def — its returns are its own
                    def visit_FunctionDef(self, _n):
                        return False

                for stmt in node.body.body:
                    stmt.visit(R())
                if len(vals) < 2:
                    return False
                kinds = set()
                for v in vals:
                    if v is None or (isinstance(v, cst.Name) and v.value == "None"):
                        kinds.add("clear")
                    elif isinstance(v, cst.Name) and v.value in ("True", "False"):
                        kinds.add("bool")
                    elif isinstance(v, cst.Integer):
                        kinds.add("code")
                    else:
                        kinds.add("data")
                # a verdict shape: at least one all-clear AND one non-data signal
                if ("clear" in kinds or "bool" in kinds) and kinds & {"bool", "code"}:
                    out[node.name.value] = (path, pos[node].start.line)
                return False

            # ⚑ THIS EXCLUSION IS CORRECT AND IT DOES NOT FIX THE 360 ROWS — the real
            # defect is one layer down and I found it only by measuring twice more.
            # MEASURED: `check` is NOT in `verdict_returners` for `gate_status.py` or
            # `agda_lex.py` (the exclusion works), yet the sweep still reports 360
            # `check` rows.  Cause: **five MODULE-LEVEL `def check`** exist
            # (`fix_notinscope:86`, `fix_ambiguous_import:109`, `prune_leaf_opens:51`,
            # `untethered_disjunct_advisory:91`, …), so `check` enters the population
            # legitimately — and `_bare_calls` then matches EVERY bare `check(...)`
            # in the corpus, including ~30 files' test-local ones.
            #
            # **A BARE NAME IS NOT A DECIDABLE UNIT** — the same finding as §22, where
            # `def_index` keyed `_-ℤ_` and `-ℤ_` both as `-ℤ` and would have renamed
            # 18 operators correctly-per-the-plan and wrongly-per-the-language.  The
            # honest fix is a SCOPE-AWARE call resolver (does this call site resolve
            # to THAT def?), which is a real build and is filed as `T20` rather than
            # patched here.  Until then `--discards` over-reports on any name that is
            # both a module-level def somewhere and a local helper elsewhere.
            #
            # ⚑ A TEST-LOCAL ASSERTION HELPER IS NOT A SHARED AUTHORITY, AND IT WAS
            # ~360 OF 362 ROWS.  Nearly every `_selftest` defines `check(name, got,
            # want)`; bare-calling it IS its purpose (it appends to a case list), and
            # its return exists for the rare caller that wants it.  Such a helper has
            # one scope and one author, so it cannot be an inert SHARED guard — while
            # 360 of its rows bury the one real finding, which is §60's rule exactly:
            # *a predicate carrying false positives does not merely over-report, it
            # HIDES the true positives among them.*
            #
            # ⚑ AND I "VERIFIED" THIS EXCLUSION FROM A ONE-FILE SAMPLE AND WAS WRONG.
            # `verdict_returners([agda_defs.py])` reported `check not in population`,
            # so I wrote that nested defs were already excluded.  The full ledger then
            # showed ~360 `check` rows from `agda_lex`, `conduit_resolve`,
            # `split_pipeline` and 30 others — same name, different nesting depth than
            # the file I sampled.  *A one-file sample generalised to a corpus claim*,
            # the same shape as §41's 25-file sample reading 12% where the population
            # was 19%.  Fifth wrong attribution of this sitting.

        try:
            wrapper.visit(V())
        except Exception:
            continue
    return out


def reifies(paths=None):
    """[(path, line, name, kind, why)] — defs that RETURN A MATERIALIZED COLLECTION.

    ⚑ THE MODE THE ⟡sorted-stream-carrier CENSUS NEEDED AND DID NOT HAVE.  `--dead` finds
    unwired defs, `--discards` finds thrown-away values, `--relalg` finds withheld
    relational algebra at an EXPRESSION; none of them answers *which functions hand back a
    whole set/dict/list where a stream would do*.  That census was assembled by hand from
    `--layout` + `--calls` + reads — judgement in the turn, which the standing rule forbids,
    committed while planning the arc whose subject is exactly this.

    `kind` is what is returned (`set` / `dict` / `list` / `sorted` / `frozenset` / `tuple`)
    and `why` is the shape that made it one:

      returns-literal    `return {...}` / `[...]` — built in place
      returns-comp       `return {x for ...}` / `{k: v for ...}` / `[... for ...]`
      returns-call       `return set(...)` / `sorted(...)` / `dict(...)` / `list(...)`
      returns-accum      returns a name that was built by `.append`/`.add`/`|=`/`[k]=`
      returns-sorted     ⚑ returns `sorted(...)` — an ORDER the caller cannot see

    ⚑ `returns-sorted` IS THE ROW THAT MATTERS AND IT IS WHY THIS IS NOT JUST `--discards`
    INVERTED.  A def that sorts and returns has ALREADY PAID for an order and then thrown
    away the fact — so its callers re-sort defensively.  That double sort is witnessed one
    hop apart in this very corpus: `agda_defs.import_index()` sorts at :1732 and DECLARES it
    in its docstring, and `importers_of()` re-sorts at :1757 anyway.  The knowledge did not
    survive one function call because there was nowhere on the VALUE to put it.
    `jea/metalanguage/sorted_stream.py` is where it goes.

    ⚑ THIS REPORTS A SHAPE, NEVER A VERDICT.  A reification is not a defect — `from_set`
    in `sorted_stream` materializes deliberately, because somebody must pay the sort once
    at the named producer.  What the census is for is finding where that payment happens
    MORE THAN ONCE along a chain.  Deliberately coarse in the safe direction: an accumulator
    reached through an alias or built by a helper is missed (under-reports).

    Carries `reifies.skipped` / `reifies.population` so a zero cannot read as a clean tree —
    the confident-zero class `_report_skipped` exists for.
    """
    files = list(paths or _pycodemod_core.py_files())
    reifies.population = len(files)                      # noqa: attribute on a function
    reifies.skipped = []
    out = []
    if cst is None:
        reifies.skipped = [(p, "no-libcst", "libcst not importable") for p in files]
        return out

    _BUILDERS = {"set": "set", "frozenset": "frozenset", "dict": "dict", "list": "list",
                 "sorted": "sorted", "tuple": "tuple", "Counter": "dict", "defaultdict": "dict"}
    _GROWS = {"append", "add", "extend", "update", "setdefault"}

    for path in files:
        try:
            src = open(path, encoding="utf-8").read()
            mod = cst.parse_module(src)
            wrapper = cst.metadata.MetadataWrapper(mod)
            pos = wrapper.resolve(cst.metadata.PositionProvider)
        except Exception as e:                            # noqa: BLE001
            reifies.skipped.append((path, "unreadable", f"{type(e).__name__}: {e}"))
            continue

        class V(cst.CSTVisitor):
            METADATA_DEPENDENCIES = (cst.metadata.PositionProvider,)

            def __init__(self):
                super().__init__()
                self.fn = []                              # def-name stack
                self.grown = []                           # names grown in the current def

            def visit_FunctionDef(self, node):
                self.fn.append(node.name.value)
                self.grown.append(set())

            def leave_FunctionDef(self, node):
                self.fn.pop()
                self.grown.pop()

            # ── accumulation: `x.append(...)`, `x |= ...`, `x[k] = ...` ──────────
            def visit_Call(self, node):
                f = node.func
                if (isinstance(f, cst.Attribute) and f.attr.value in _GROWS
                        and isinstance(f.value, cst.Name) and self.grown):
                    self.grown[-1].add(f.value.value)

            def visit_AugAssign(self, node):
                if isinstance(node.target, cst.Name) and self.grown:
                    self.grown[-1].add(node.target.value)

            def visit_Assign(self, node):
                for t in node.targets:
                    tgt = t.target
                    if isinstance(tgt, cst.Subscript) and isinstance(tgt.value, cst.Name) \
                            and self.grown:
                        self.grown[-1].add(tgt.value.value)

            def visit_Return(self, node):
                if not self.fn or node.value is None:
                    return
                v, name, line = node.value, self.fn[-1], pos[node].start.line

                def emit(kind, why):
                    out.append((path, line, name, kind, why))

                if isinstance(v, cst.Set):
                    return emit("set", "returns-literal")
                if isinstance(v, cst.Dict):
                    return emit("dict", "returns-literal")
                if isinstance(v, cst.List):
                    return emit("list", "returns-literal")
                if isinstance(v, cst.SetComp):
                    return emit("set", "returns-comp")
                if isinstance(v, cst.DictComp):
                    return emit("dict", "returns-comp")
                if isinstance(v, cst.ListComp):
                    return emit("list", "returns-comp")
                if isinstance(v, cst.Call) and isinstance(v.func, cst.Name):
                    b = v.func.value
                    if b in _BUILDERS:
                        # ⚑ `sorted` gets its OWN why, not folded into returns-call: an
                        # order was paid for and then discarded, which is the actionable row.
                        return emit(_BUILDERS[b],
                                    "returns-sorted" if b == "sorted" else "returns-call")
                if isinstance(v, cst.Name) and self.grown and v.value in self.grown[-1]:
                    return emit("accum", "returns-accum")

        try:
            wrapper.visit(V())
        except Exception as e:                            # noqa: BLE001
            reifies.skipped.append((path, "visit-failed", f"{type(e).__name__}: {e}"))
            continue
    return sorted(out)


reifies.skipped = []
reifies.population = 0


def funcnames(paths=None):
    """[(path, line, caller, name, kind)] — every SQLAlchemy `func.<name>(...)` call, graded by
    whether Core will TRANSLATE it per dialect or pass it through VERBATIM.

    ⚑⚑ THE GATE THAT SHOULD HAVE CAUGHT ⟡synth-agda-group-concat READ GREEN OVER IT.
    `pycodemod --portable jea/metalanguage/autocorr_synth.py` reports `0 blocking site(s)` on
    the file that raised `UndefinedFunction: group_concat` on every invocation — because
    `--portable` EXPLAINs raw SQL LITERALS and that query is built by Core, never a string.
    Meanwhile `jea/metalanguage/store.py`'s migration-path paragraph filed `GROUP_CONCAT`
    under *raw-SQL* sites that must be rewritten, and declared a Core statement
    "dialect-agnostic BY CONSTRUCTION".
    ⚑ CITED BY MODULE AND CONCEPT, NOT BY LINE RANGE. This docstring said `store.py:23-29`
    until 2026-08-19, when adding the correction to that very paragraph moved it — a prose
    pointer that went stale in the same edit that made it true. A line number is a fact about
    a file's current shape; the module plus what the passage SAYS survives an edit to it.

    **Both are right about what they cover and neither covers `func.`** — which is where the
    declared line between "ports for free" and "must be rewritten" stops holding.

    ⚑⚑⚑ AND THE KIND IS NOT "PORTABLE vs BROKEN", WHICH IS WHAT I FIRST ASSUMED. MEASURED
    against SQLAlchemy 2.x (bounded probe, compile-only, no store):

        func.totally_made_up_xyz(c)  ->  "totally_made_up_xyz(c)"   on BOTH dialects
        func.string_agg(c)           ->  "string_agg(c)"            on BOTH dialects

    An invented name compiles silently, and `string_agg` — perfectly valid postgres — sits in
    the SAME bucket as the invented one. There are **52** names in SQLAlchemy's generic
    registry and NO per-dialect registry to check against (`_registry` has exactly one key,
    `_default`). So this census CANNOT say a function does not exist, and a mode claiming to
    would be inventing a verdict its instrument cannot support.

    What it CAN say, exactly:

      generic    the name resolves to a typed `GenericFunction` subclass — SQLAlchemy owns the
                 per-dialect spelling, so it genuinely "ports for free" (`count`, `max`,
                 `coalesce`, `array_agg`, …)
      verbatim   the name is passed through UNCHANGED — a plain `Function` with NullType. It
                 may be perfectly valid for the CURRENT tenant (`string_agg` is), but Core is
                 not translating it, so it is dialect-SPECIFIC and unverified. This is the
                 population a migration must re-read; `group_concat` was one of these.

    ⚑ SO THE VERDICT IS "UNVERIFIED BY CORE", NOT "WRONG" — and the distinction is the whole
    point. `report presence, never absence`: a verbatim row is a fact about what Core checked,
    not a claim about the database.
    """
    files = list(paths or _pycodemod_core.py_files())
    funcnames.population = len(files)                   # noqa: attribute on a function
    funcnames.skipped = []
    out = []
    if cst is None:
        funcnames.skipped = [(p, "no-libcst", "libcst not importable") for p in files]
        return out

    generic = _generic_func_names()

    for path in files:
        try:
            src = open(path, encoding="utf-8").read()
            mod = cst.parse_module(src)
            wrapper = cst.metadata.MetadataWrapper(mod)
            pos = wrapper.resolve(cst.metadata.PositionProvider)
        except Exception as e:                          # noqa: BLE001
            funcnames.skipped.append((path, "unreadable", f"{type(e).__name__}: {e}"))
            continue

        class V(cst.CSTVisitor):
            METADATA_DEPENDENCIES = (cst.metadata.PositionProvider,)

            def __init__(self):
                super().__init__()
                self.fn = []

            def visit_FunctionDef(self, node):
                self.fn.append(node.name.value)

            def leave_FunctionDef(self, node):
                self.fn.pop()

            def visit_Call(self, node):
                f = node.func
                # ⚑ RECEIVER-SCOPED, and that is load-bearing: `--attr func` reports 111 sites
                # of which almost all are libcst's `node.func`, an unrelated attribute with the
                # same spelling. A name-scoped census here would be the `--calls emit` defect
                # (a fact about the METHOD read as a fact about the substrate) with the two
                # populations reversed — noise burying the signal rather than hiding it.
                if not (isinstance(f, cst.Attribute)
                        and isinstance(f.value, cst.Name) and f.value.value == "func"):
                    return
                name = f.attr.value
                out.append((path, pos[node].start.line,
                            self.fn[-1] if self.fn else "<module>", name,
                            "generic" if name in generic else "verbatim"))

        try:
            wrapper.visit(V())
        except Exception as e:                          # noqa: BLE001
            funcnames.skipped.append((path, "visit-failed", f"{type(e).__name__}: {e}"))
            continue
    return sorted(out)


funcnames.skipped = []
funcnames.population = 0


def _generic_func_names():
    """{name} — SQLAlchemy's generic (dialect-translated) function registry, ASKED not listed.

    ⚑ THE AUTHORITY IS THE LIBRARY, NEVER A ROSTER HERE. A hardcoded list of 52 names is the
    frozen-roster defect this repo has recorded three times: it would go stale on a SQLAlchemy
    upgrade and report a newly-generic function as verbatim forever.

    ⚑⚑ IT READS A PRIVATE NAME (`_registry`), SO IT MUST FAIL LOUD, NOT EMPTY. My first cut
    returned `set()` on any failure and called that "loud" — it is not: an empty registry
    grades EVERY call `verbatim`, which reads as a big honest finding and is actually the
    instrument being blind. That is the confident-answer shape with the sign flipped. A
    private API that moved is a fact about the METHOD and must be raised.
    """
    from sqlalchemy.sql.functions import _registry
    names = set(_registry.get("_default", {}))
    if not names:
        raise RuntimeError(
            "sqlalchemy.sql.functions._registry['_default'] is empty or has moved — "
            "cannot grade func.<name> calls. This is a fact about the QUERY (a private "
            "API changed under us), not about the corpus; refusing rather than grading "
            "every call 'verbatim'.")
    return names


def resorts(paths=None):
    """[(path, line, caller, callee, why)] — a SECOND sort over a value already sorted upstream.

    ⚑ THE CONSUMER ARM `--reifies` DID NOT HAVE, AND ITS ABSENCE WAS THE GATE'S STATED BLIND
    SPOT.  `reifies` censuses PRODUCERS — defs that pay for an order and drop the fact.  It
    cannot see the other end, so `check_sorted_order` green means "no NEW order was made
    unsayable", never "the corpus does not double-sort".  Those are different claims and the
    gate says so; this closes the difference.

    ⚑⚑ AND IT IS A SPAN QUERY, WHICH IS WHY IT COULD NOT BE A ROW IN THE PRODUCER CENSUS.
    "Is this sort redundant" is not a property of the sort SITE — it is a property of the
    PAIR (producer, consumer), so answering it needs both endpoints related.  That is the
    operator's Π-typing correction as a census: *you cannot just look at boundaries, you have
    to look at spans across boundary-pairs.*  A per-site predicate can only ever report "here
    is a sort", which is the count `--relalg` already gives.

    Two kinds, and the second is the one that matters:

      resort-of-sorted   `sorted(f(...))` where `f` is in the `returns-sorted` census — the
                         callee already sorted, so this pays twice for the SAME order
      resort-rekeyed     the same, but this call passes `key=` / `reverse=` — a DIFFERENT
                         order, so it is NOT redundant

    ⚑ THE SECOND KIND EXISTS SO THE FIRST STAYS HONEST, and it is not a technicality: I read
    `_pycodemod_query.swallows()` (`return sorted(rows)`) as a redundant re-sort of a
    `py_files()` walk and was WRONG — the rows are sorted on the whole row tuple, a different
    key from the path order they arrived in.  A census that reported both as one number would
    have banked that error.  A re-key is reported, never counted as debt.

    ⚑ DELIBERATELY COARSE, IN THE SAFE DIRECTION.  Only a DIRECT `sorted(callee(...))` is
    seen — a value bound to a name and sorted three lines later is missed, as is a callee
    reached through an alias or an attribute.  UNDER-reports; it will not cry wolf.  The
    honest limit is stated because the whole point of the pair is that neither end alone is
    a verdict.
    """
    files = list(paths or _pycodemod_core.py_files())
    resorts.population = len(files)                     # noqa: attribute on a function
    resorts.skipped = []
    out = []
    if cst is None:
        resorts.skipped = [(p, "no-libcst", "libcst not importable") for p in files]
        return out

    # ⚑ THE PRODUCER CENSUS IS THE INPUT, NEVER A SECOND WALK WITH ITS OWN IDEA OF
    # "returns sorted".  One capability, one authority — the `agda_files()`-as-four-bodies
    # defect is what a private re-implementation here would be.
    #
    # ⚑⚑ THE PRODUCER SET IS THE UNION OF THE CORPUS AND THE WALKED PATHS, AND GETTING THIS
    # WRONG BROKE THE MODE'S OWN CASES.  My first cut read `reifies(None)` alone, arguing a
    # scoped producer set would make the join report a fact about the SCOPE (the `--dead`
    # scoped-run trap).  That half is TRUE and is why the corpus is always included.  But it
    # is not the whole span: a caller and its callee can BOTH live outside the corpus — a
    # tempdir fixture, a `--package` read, a vendored tree named explicitly — and then the
    # corpus-only producer set knows neither end, so the mode reports ZERO on a file that
    # contains a textbook double sort.  Measured: three cases pinning the redundant/re-keyed
    # split all returned None until the union went in.
    #
    # ⚑ A SPAN NEEDS BOTH ENDPOINTS REACHABLE, WHICH IS THE WHOLE POINT — scoping either end
    # away turns a pair query back into a site query that can only ever answer "here is a
    # sort".  Union, so neither endpoint can be scoped out of existence.
    # ⚑⚑ MEMOISED, AND THE UNMEMOISED VERSION DID NOT FINISH IN TWO MINUTES. `reifies` over
    # the union is a full-corpus CST walk; calling it per `resorts()` invocation is §55's
    # defect exactly — the shape `_bare_calls` above already records ("the per-name version
    # re-parsed every file once per name... the first run did not finish inside two minutes").
    # Measured here 2026-08-19: `--resorts <one file>` returned instantly before a selftest
    # case added a second call site, then BOTH timed out. The work was always repeated; a
    # second caller is what made it visible.
    # ⚑ KEYED BY THE RESOLVED POPULATION, so a scoped call cannot read a whole-corpus cache —
    # the §51 scoped-run-clobber class at cache granularity, per `_bare_calls`' own note.
    _producer_files = tuple(dict.fromkeys(list(_pycodemod_core.py_files()) + files))
    if _producer_files in _PRODUCER_CACHE:
        sorted_defs, _prod_pop, _prod_skip = _PRODUCER_CACHE[_producer_files]
    else:
        sorted_defs = {name for _p, _l, name, _k, why in reifies(list(_producer_files))
                       if why == "returns-sorted"}
        _prod_pop, _prod_skip = reifies.population, list(reifies.skipped)
        _PRODUCER_CACHE[_producer_files] = (sorted_defs, _prod_pop, _prod_skip)
    # ⚑ TWO POPULATIONS, TWO ACCOUNTINGS, AND THEY MUST NOT BE MERGED.  `reifies` stamps its
    # own `population`/`skipped` for the PRODUCER walk; `resorts` owns the CONSUMER walk's.
    # Copying the producer's skips into `resorts.skipped` would report files this walk never
    # tried to read as files it failed on — a population confusion inside the mode whose
    # subject is relating two populations.  What the consumer arm owes its reader is the
    # producer's *incompleteness*, kept separate and named as such.
    resorts.producer_population = _prod_pop
    resorts.producer_skipped = _prod_skip

    for path in files:
        try:
            src = open(path, encoding="utf-8").read()
            mod = cst.parse_module(src)
            wrapper = cst.metadata.MetadataWrapper(mod)
            pos = wrapper.resolve(cst.metadata.PositionProvider)
        except Exception as e:                          # noqa: BLE001
            resorts.skipped.append((path, "unreadable", f"{type(e).__name__}: {e}"))
            continue

        class V(cst.CSTVisitor):
            METADATA_DEPENDENCIES = (cst.metadata.PositionProvider,)

            def __init__(self):
                super().__init__()
                self.fn = []

            def visit_FunctionDef(self, node):
                self.fn.append(node.name.value)

            def leave_FunctionDef(self, node):
                self.fn.pop()

            def visit_Call(self, node):
                f = node.func
                if not (isinstance(f, cst.Name) and f.value == "sorted"):
                    return
                if not node.args:
                    return
                inner = node.args[0].value
                if not isinstance(inner, cst.Call):
                    return
                g = inner.func
                callee = (g.attr.value if isinstance(g, cst.Attribute)
                          else g.value if isinstance(g, cst.Name) else None)
                if callee not in sorted_defs:
                    return
                # a `key=`/`reverse=` on the OUTER sorted() means a different order
                rekeyed = any(a.keyword is not None and
                              a.keyword.value in ("key", "reverse") for a in node.args)
                out.append((path, pos[node].start.line,
                            self.fn[-1] if self.fn else "<module>", callee,
                            "resort-rekeyed" if rekeyed else "resort-of-sorted"))

        try:
            wrapper.visit(V())
        except Exception as e:                          # noqa: BLE001
            resorts.skipped.append((path, "visit-failed", f"{type(e).__name__}: {e}"))
            continue
    return sorted(out)


resorts.skipped = []
resorts.population = 0
#: The PRODUCER walk's accounting, named separately — see the union comment in the body.
resorts.producer_skipped = []
resorts.producer_population = 0


def discards(name, paths=None):
    """([(path, line)] USING the return value, [(path, line)] DISCARDING it).

    ⚑ THE THIRD QUESTION IN THIS FAMILY, AND IT FOUND A LIVE INERT GUARD ON THE FIRST
    RUN — in a gate written minutes earlier, by me, while quoting the lesson it breaks.
    `ratchet.check_argv` RETURNS an exit code rather than raising; its docstring states
    the contract (`if (rc := check_argv(...)) is not None: return rc`).  A caller that
    writes the bare statement gets the complaint PRINTED and the gate RUNS ANYWAY.  The
    guard is present, greppable, mentioned in the docstring — and inert.

    `--calls` finds the sites; `--forwards` checks what goes IN; neither can see what
    comes OUT being dropped.  That is the shape of every guard-degradation this arc has
    recorded (§52's `hasattr` fallback to an empty set, §60's armed-but-inert snapshot
    helpers, §7a's write guard that six gates routed around): **the call is there and
    its verdict is not consumed.**  A census that verifies PRESENCE cannot see it.

    A call is USING its value when it is anything other than a bare expression
    statement — assigned, returned, tested, passed on, walrus-bound.  Deliberately
    coarse in the safe direction: a value consumed in any way at all counts as used,
    so this UNDER-reports rather than crying wolf on an idiom it does not know.

    Reports BOTH sides, for the reason `forwards` states: a bare list of the broken
    ones reads as the whole population.
    """
    rows = _bare_calls(tuple(paths) if paths else None)
    dropped = sorted(rows.get(name, set()))
    using = sorted({(p, line) for p, kind, _n, line in scan(list(paths or _pycodemod_core.py_files()), name)
                    if kind == "call"} - set(dropped))
    return using, dropped


def _bare_calls(paths=None):
    """{callee-name -> {(path, line)}} for every BARE-STATEMENT call in the corpus.

    ⚑ ONE PASS OVER THE CORPUS, MEMOISED — because the per-name version was §55's
    defect exactly.  `discards(name)` re-parsed every file once per name; sweeping
    ~100 verdict-returners meant ~100 identical CST walks, and the first run of the
    T19 sweep did not finish inside two minutes.  §55's own lesson is the one that
    applies: *before reaching for concurrency, check whether the work is REPEATED* —
    there, memoising `parse_tree()` took 300s+ to 2.7s.  Parallelising 100 redundant
    walks would only have made the same mistake run faster.

    Keyed by the resolved population so a scoped call cannot read a whole-corpus
    cache (the §51 scoped-run-clobber class, at cache granularity).
    """
    key = paths
    if key in _BARE_CACHE:
        return _BARE_CACHE[key]
    out: dict = {}
    if cst is None:
        _BARE_CACHE[key] = out
        return out
    for path in list(paths or _pycodemod_core.py_files()):
        try:
            src = open(path, encoding="utf-8").read()
            mod = cst.parse_module(src)
            wrapper = cst.metadata.MetadataWrapper(mod)
            pos = wrapper.resolve(cst.metadata.PositionProvider)
        except Exception:
            continue

        class V(cst.CSTVisitor):
            METADATA_DEPENDENCIES = (cst.metadata.PositionProvider,)

            def visit_Expr(self, node):
                # an Expr IS the bare-statement case: the value goes nowhere
                call = node.value
                if not isinstance(call, cst.Call):
                    return
                fn = call.func
                nm = (fn.attr.value if isinstance(fn, cst.Attribute)
                      else fn.value if isinstance(fn, cst.Name) else None)
                if nm:
                    out.setdefault(nm, set()).add((path, pos[node].start.line))

        try:
            wrapper.visit(V())
        except Exception:
            continue
    _BARE_CACHE[key] = out
    return out


def shape_sites(pattern, paths=None, in_code_only=True):
    """[(path, line, text)] — where a SOURCE SHAPE occurs, located.

    ⚑ A FINDING WITHOUT A LOCATION MAKES THE OPERATOR HUNT (user, 2026-08-03:
    *"sounds like grounds for a tooling fix"*).  F5's class guard found six sites
    of the `or None` defect and printed the MATCHED TEXT — so I then spent three
    commands (`--key`, `--calls`, two `Read`s) locating four of them by hand, which
    is the reprocessing loop the standing rule forbids, committed while fixing a
    defect about exactly that.

    Every sibling mode reports `file:line`; the class-scan reported strings. This
    closes that: a shape query answers WHERE, like the rest of the toolkit.

    ⚑ COMMENTS AND DOCSTRINGS ARE EXCLUDED BY DEFAULT, and that is not cosmetic.
    My own ⚑ comment describing the `or None` defect MATCHED the scan for it — a
    sixth "site" that was prose about the other five.  Same prose-vs-code
    discrimination that makes `--calls` beat grep, at the line layer.
    `in_code_only=False` asks the other question (does anything MENTION this),
    which is legitimate and different.

    The pattern is a regex over source LINES, deliberately: the defects this
    finds are spellings (`X or None`, `len({...}) file(s)`), not AST shapes — an
    AST query would need a matcher per defect, which is the judgement-in-the-turn
    this exists to remove."""
    rx = re.compile(pattern)
    # ⚑ THE PRE-FILTER SILENTLY DEFEATED `^` AND `$`, and I hit it TWICE before
    # fixing it — once writing `^\s*(if )?rc\b` (0 sites, wrong), once writing
    # `^if __name__` (0 sites, wrong), and both times I rewrote the QUERY rather
    # than suspecting the TOOL.  The per-line match below is anchor-correct; the
    # whole-file `rx.search(src)` above it is not, because without `re.M` a `^`
    # matches only at offset 0 of the entire source.  So an anchored pattern was
    # filtered out before any line was ever examined — a fast path that changed
    # the answer, which is the worst kind.
    #
    # The pre-filter is worth keeping (it skips tokenising most of the corpus),
    # so it is compiled with `re.M` while the per-line matcher stays exact: the
    # filter must be a SUPERSET of what the real match accepts, never a peer.
    pre = re.compile(pattern, rx.flags | re.M)
    out = []
    for p in (paths if paths is not None else _pycodemod_core.py_files()):
        try:
            src = open(p, encoding="utf-8", errors="replace").read()
        except OSError:
            continue
        if not pre.search(src):
            continue
        code = _code_lines(src) if in_code_only else set(
            range(1, src.count("\n") + 2))
        for i, line in enumerate(src.splitlines(), 1):
            if i in code and rx.search(line):
                out.append((p, i, line.strip()))
    return out


# ⚑ `cli_flags` LIVED HERE FOR ONE TURN AND IS DELETED — a REINVENTION, and the
# finding it produced is kept because the reinvention is the more useful record.
#
# THE QUESTION WAS REAL.  The dead-capability guard (written after
# `split_pipeline.rewire_only` shipped 1 def / 0 calls) is a SUBSTRING SEARCH over
# `inspect.getsource(main)`, so it cannot see a flag dispatched from another scope.
# MEASURED 2026-08-17: `split_pipeline` dispatches `--rewire-only`/`--retire` from
# `main()` and `--diagnose`/`--verify`/`--census`/`--last`/`--why`/`--unblock`/
# `--ready` from the module-level `__main__` block — a `--ready` guard written
# against `getsource(main)` FAILED, correctly, for a reason about the file's
# structure rather than about the flag.
#
# ⚑ BUT `scratch/toolmodes.py:408 literal_flags` ALREADY ANSWERED IT, AND BETTER.
# It is `ast`-anchored to argv and recognises the idioms a `"--x" in argv` matcher
# cannot: positional equality (`argv[0] == "--x"`), membership against a tuple
# literal, `add_argument`, `ratchet.check_argv`'s declared `known` sets, all-flag
# dispatch tables — and `_argv_aliases` (:389-405), a fixpoint over assignments
# whose RHS reaches argv, which is exactly the `flags = set(argv)` / `cmd = argv[0]`
# chain that defeated the version deleted here.  Measured coverage gap: this matcher
# reported ZERO flags for `scripts/buildtime.py` (8), `scripts/ddl_lifecycle.py` (6)
# and `scripts/proofcost.py` (8), and reported a garbage flag named `--` for
# `scratch/estate/mat260/tools/buildtime.py:81`.
#
# ⚑ AND THE REUSE-SEARCH THAT WOULD HAVE CAUGHT IT WAS RUN ON THE WRONG NOUN.
# `--calls flags` and `--calls _dispatch` were both asked; neither names the
# CAPABILITY, and `toolmodes --find` — the mode built precisely to answer "which
# tool has this?" — was not consulted until after the code existed.  That is the
# name-scoped-not-capability-scoped miss CLAUDE.md records, committed against the
# tool that exists to prevent it.
#
# WHAT SURVIVES AS A REAL GAP: `literal_flags` returns bare SETS — no line, no
# scope — so the split-dispatch fact above is still unreadable from any tool.  The
# fix is position+scope ON `literal_flags`' recognizer, never a second matcher.
# Filed rather than built, because building it here would repeat the error.


# ⚑ `archive_defs` AND `archive_source` LIVED HERE AND ARE DELETED — the finding
# they carried is kept, the implementations are not.
#
# The finding: READING A REFERENCE IMPLEMENTATION HAD NO COMMAND (2026-08-02).
# Handed `fuel-series.tar.gz`, I reached for `mkdir && tar xzf && find | head` --
# four commands, a pipe, and a directory to clean up.  That gap was real.
#
# ⚑ BUT THE FIX WAS THE WRONG SHAPE, AND ITS WRONGNESS COMPOUNDED IN ONE TURN.
# `archive_defs` answered "what does this define"; when I then wanted a BODY I
# bolted `--show` onto it rather than noticing the pattern.  Two functions
# re-walking members that `_scan_defs` already walks, and a third question would
# have wanted a third.  An archive is not a QUESTION, it is a SCOPE -- so
# `corpus` opens it, `_dispatch` runs inside, and every existing mode answers
# about it with no per-mode work.  `--archive X --dead`, `--archive X --calls`,
# `--archive X --imports`, and whatever mode is added tomorrow.
#
# ⚑ The "does not extract" reasoning is also retired ON PURPOSE, not forgotten:
# it protected against a reference being written where a reader might edit an
# uncovered copy.  A temp tree removed by the `with` does not have that property,
# and carrying a constraint into a design it was not written for is the stale
# judgement-as-code this file's `_roots` comment already records.


def available(mods):
    """[(module, verdict, detail)] — is this library IMPORTABLE, and which one.

    ⚑ THE REUSE-SEARCH'S FIRST QUESTION HAD NO COMMAND (user, 2026-08-02: *"how
    much of this is us reinventing networkx?"*).  I had just hand-written a BFS
    reachability closure -- which is `nx.descendants` -- and the check I reached
    for was `python3 -c "import networkx"`, i.e. answering a standing question
    at a shell.  "Before building X, does X already exist here" is asked before
    every build in this repo; it deserves an instrument.

    ⚑ AND IT REPORTS THE VERSION AND FILE, NOT A BOOLEAN.  "Available" is not
    one fact: a vendored copy, a venv install and a system package behave
    differently under a hook (`reference_uv_runs_python_with_deps` records that
    `uv run --with` fetches on the fly, so ABSENT-here is not ABSENT-always).
    Naming WHICH module answered is what keeps a later reader from re-deriving
    it -- the same reason `--rivals` names the callee."""
    out = []
    for m in mods:
        try:
            mod = __import__(m)
        except Exception as e:
            out.append((m, "ABSENT", type(e).__name__))
            continue
        ver = getattr(mod, "__version__", "(no __version__)")
        where = getattr(mod, "__file__", "(builtin)") or "(namespace)"
        out.append((m, "PRESENT", "%s  %s" % (ver, where)))
    return out


def _cached_defs(path):
    """[(name, line, delegating)] for one file — MEMOISED ON CONTENT HASH.

    ⚑ SCOPING TO FIT THE INSTRUMENT IS NOT FIXING THE INSTRUMENT (user,
    2026-08-02: *"not a problem or reason not to do the analysis.  But a good
    reason to hash-cons and memoize"*).  A full-corpus CST parse took T23 past
    a 120s timeout twice, and my response was to narrow the corpus to
    `scratch/scripts/catalog` -- which makes the question cheaper by making it
    smaller, i.e. answers a different question.  The parse is a PURE FUNCTION
    of file content, so it is cacheable and the scope can stay whole.

    ⚑ KEYED BY CONTENT **AND DERIVER**, NOT MTIME OR PATH.  An mtime key
    re-parses on every checkout and `touch`; a path key goes stale silently on
    edit.  The sha of the bytes is fresh with respect to the INPUT -- the same
    reasoning as `run_selftests.population_stamp`.

    ⚑ AND THIS DOCSTRING USED TO STOP THERE, CLAIMING THE BYTES WERE "the only
    key that is exactly as fresh as the answer".  That is false across a libcst
    upgrade: same bytes, different derivation, and a content-only key hands back
    the OLD artifact with no signal.  Corrected by cassian-observability
    (2026-08-03) reviewing the ask I sent them, which quoted this very sentence
    as the design to copy.  The key now carries `_DERIVER` so a version or
    schema change MISSES and re-derives; a stale read is unrepresentable rather
    than unlikely.

    The cache is a plain directory of json blobs, gitignored, so a cold clone
    pays the parse once and every later run is a hash lookup."""
    import hashlib
    import json
    try:
        raw = open(path, "rb").read()
    except OSError:
        return []
    # ⚑ A CONTENT HASH IS FRESH W.R.T. THE INPUT, NOT THE DERIVATION — and my own
    # docstring above claims more than that.  "the sha of the bytes is the only
    # key that is exactly as fresh as the answer" is FALSE across a libcst
    # upgrade: same file bytes, different parse, and a pure content key
    # deserialises the OLD artifact silently (cassian-observability, 2026-08-03,
    # correcting the ask I sent them).  Today this stores a plain JSON list so a
    # bump could not corrupt it — but the RULE is what gets copied, and it is the
    # rule that is wrong.
    #
    # Folding the deriver's identity into the key makes a stale read
    # UNREPRESENTABLE rather than merely unlikely: a libcst bump or a change to
    # the record shape MISSES and re-derives, which is the property the docstring
    # was already claiming.  `_SCHEMA` is bumped by hand when the tuple shape
    # changes; the library version is read, not declared.
    key = hashlib.sha1(raw + _DERIVER.encode()).hexdigest()
    blob = os.path.join(_PARSE_CACHE, key[:2], key[2:] + ".json")
    try:
        with open(blob, encoding="utf-8") as fh:
            return [tuple(r) for r in json.load(fh)]
    except Exception:
        pass
    out = _scan_defs(raw.decode("utf-8", "replace"))
    try:
        # ⚑ THE WRITER OWNS ITS TRACKING STATUS.  A parse cache is machine-local
        # derived state, not repository content -- the same rule
        # `run_selftests._ensure_ignored` follows for its ledger, and the reason
        # is identical: the tool that creates an artifact is the only thing that
        # reliably knows what it is.
        _ignore_cache()
        os.makedirs(os.path.dirname(blob), exist_ok=True)
        with open(blob, "w", encoding="utf-8") as fh:
            json.dump(out, fh)
    except OSError:
        pass                             # a cache miss must never fail a query
    return out


def _scan_defs(src):
    """[(name, line, delegating)] — the single CST pass every query shares."""
    if cst is None:
        return []
    try:
        mod = cst.parse_module(src)
        wrapper = cst.metadata.MetadataWrapper(mod)
        pos = wrapper.resolve(cst.metadata.PositionProvider)
    except Exception:
        return []
    out = []

    class V(cst.CSTVisitor):
        METADATA_DEPENDENCIES = (cst.metadata.PositionProvider,)

        def visit_FunctionDef(self, node):
            stmts = [s for s in node.body.body
                     if not (isinstance(s, cst.SimpleStatementLine)
                             and len(s.body) == 1
                             and isinstance(s.body[0], cst.Expr)
                             and isinstance(s.body[0].value, cst.SimpleString))]
            delegating = (
                len(stmts) == 1
                and isinstance(stmts[0], cst.SimpleStatementLine)
                and len(stmts[0].body) == 1
                and isinstance(stmts[0].body[0], cst.Return)
                and isinstance(stmts[0].body[0].value, cst.Call))
            out.append((node.name.value, pos[node].start.line, delegating))
            return True

    wrapper.visit(V())
    return out


def collision_kinds(paths=None):
    """[(kind, [(name, sites), ...])] — collisions PARTITIONED BY RESOLUTION.

    ⚑ THE MOVE IS DECOMPOSITION, NOT SCOPING (user, 2026-08-02: *"the move is
    decomposition"*).  Handed 396 colliding names I narrowed the CLAIM to the
    294 in `scratch/scripts/catalog` -- deciding the rest "were not the defect"
    and shrinking the target to fit.  That is not mine to decide, and the
    honest move is the one A5 already demonstrated: a large population with
    several resolutions is SEVERAL ITEMS, not one item with a smaller claim.
    Every key stays in the census; each part becomes workable.

    ⚑ AND DIRECTORY IS A LOCATION, NOT A KIND.  My first partition would have
    been "tool corpus vs the rest", which orders by where a thing sits rather
    than by what resolves it -- the same reason `added_kinds` splits ban keys
    by DIRECTIVE and not by path.  These kinds each name a different fix:

      * `local`   -- every site in ONE file.  Python scopes these apart; a
                     module-local helper reused under one name is not a shared
                     authority and nothing is ambiguous to a reader.
      * `sibling` -- sites in one directory.  A candidate lift, or a genuine
                     per-file entry point (`main`, `_selftest`).
      * `crossing`-- sites in DIFFERENT top-level trees.  This is the class
                     that bit: `leverage` in `scratch/` and `scripts/`, where a
                     reader who finds one assumes the other's contract."""
    out = {"local": [], "sibling": [], "crossing": []}
    for name, sites in collisions(paths):
        files = {p for p, _l in sites}
        if len(files) == 1:
            out["local"].append((name, sites))
            continue
        tops = {os.path.relpath(p, _pycodemod_core.ROOT).split(os.sep)[0] for p in files}
        dirs = {os.path.dirname(p) for p in files}
        if len(tops) > 1:
            out["crossing"].append((name, sites))
        elif len(dirs) > 1:
            out["crossing"].append((name, sites))
        else:
            out["sibling"].append((name, sites))
    return [(k, v) for k, v in
            sorted(out.items(), key=lambda kv: -len(kv[1])) if v]


def collisions(paths=None):
    """[(name, [(path, line), ...])] — every name with 2+ REIMPLEMENTING defs.

    ⚑ ONE CORPUS PASS, NOT ONE PER NAME.  The first cut of T23's witness called
    `rivals()` for each duplicated name -- re-parsing every file per name, which
    took the item past a 120s timeout and would have made the whole selftest
    suite unrunnable.  Same shape as plan §55's 100x defect: the work was
    REPEATED, and the fix is to do it once rather than to do it faster.

    ⚑ DELEGATING DEFS DO NOT COLLIDE.  Four one-line wrappers named
    `agda_files` are an alias family, which T12 measured as CONVERGED; counting
    them here would re-open a closed item under a new label.  Only defs with
    bodies of their own are rivals."""
    if cst is None:
        return []
    by_name = {}
    for path in list(paths or _pycodemod_core.py_files()):
        for name, line, delegating in _cached_defs(path):
            if name.startswith("_") or delegating:
                continue
            by_name.setdefault(name, []).append((path, line))
    return sorted((n, sites) for n, sites in by_name.items()
                  if len(sites) >= 2)


def collision_apex(paths=None, min_sites=2):
    """[(band, [(name, nsites, nskel, holes, labels), ...])] — collisions keyed on
    BODY STRUCTURE and graded by sharing-breadth.  ⟡apex-over-collisions.

    ⚑ `collisions()` GROUPS BY `by_name.setdefault(name, ...)` AND NEVER OPENS A
    BODY, which is why its 239 rows cannot be ranked.  78 defs named `check` and 6
    named `alphabet_size` are the SAME KIND OF ROW to it: the only key it has is
    the spelling.  That is `census-keyed-on-one-spelling` a third time, and this
    mode is the other key — the one the corpus already had.

    ⚑ AND `collision_kinds` DOES NOT CLOSE IT, THOUGH ITS OWN ⚑ BLOCK GETS ONE
    STEP FURTHER.  It says "directory is a LOCATION, not a KIND" and partitions
    local/sibling/crossing by RESOLUTION — correct, and still blind here, because
    a location partition reads paths and a real-vs-coincidence verdict needs
    bodies.  Both partitions stay: they answer different questions, and the two
    DISAGREEING is itself the finding (a `crossing` with 0 holes is a lift; a
    `sibling` with 12 is a coincidence that happens to share a directory).

    ⚑ NOTHING HERE IS NEW MACHINERY — the discriminator was already built, twice,
    and the reuse-search fired on the PLAN rather than after it.
    `jea_extrude_ir.templatize` groups units by `full_skeleton` and returns the
    HOLE COUNT: the residue positions that VARY across instances.  Zero holes is
    byte-identical structure; a high count is a coincidence wearing a shared name.
    That is a COMPUTED verdict where the alternative was a judgement in the turn.

    ⚑ THE BANDS ARE `catalog/memory/synth_apex.py`'s, AND THEY ARE NOT DECORATION.
    That tool grades a memory cluster's shared Sequitur grammar over
    sharing-breadth (universal / broad / pairwise-residue) and gates every line on
    >=2 witnesses.  The same curve applies here because the same question is being
    asked — *how broadly is this structure corroborated* — and a lift candidate
    witnessed twice is residue while one witnessed 78 times is a skeleton.
    `min_sites` is that gate; below it a "cluster" is an artifact of the census.

    ⚑ A NAME WHOSE SITES SPLIT INTO SEVERAL SKELETONS IS A BRIDGE, NOT A LIFT, and
    reporting it as one candidate would be the fragment-collapse `cluster_memories`
    gates out with its MARGIN test.  `nskel` is that split, reported rather than
    resolved: `nskel == 1` is one authority under one name, `nskel > 1` is several
    contracts sharing a spelling — which is the `crossing` hazard, now measured.
    """
    # ⚑ THE IMPORT FAILURE IS RAISED, NOT SWALLOWED, AND THAT IS THE WHOLE POINT.
    # A `try/except Exception: return []` here makes an unimportable discriminator
    # report "no structural collisions" — a false ZERO, which this repo BANKS while
    # it investigates a false positive.  The first run of this mode did exactly that:
    # 7 collisions in scope, 0 reported, and the cause invisible.  An absent
    # discriminator is a fact about the METHOD and must refuse rather than answer.
    import textwrap
    sys.path.insert(0, os.path.join(_pycodemod_core.ROOT, "jea", "metalanguage"))
    import jea_extrude_ir as _ir
    import jea_pyalg as _pyalg
    files = list(paths or _pycodemod_core.py_files())
    rows = []
    for name, sites in collisions(files):
        if len(sites) < min_sites:
            continue
        # ⚑ SCOPE `source_of` TO THE COLLIDING FILES, NOT THE CORPUS.  It reparses
        # every path it is handed, and the sites are already known — handing it the
        # whole corpus per name is the repeated-work shape `collisions`' own ⚑ block
        # records paying down once already.
        # ⚑ DEDENT, OR EVERY METHOD SILENTLY SCORES `no-shared-skeleton`.  `source_of`
        # returns the body at its ORIGINAL indentation, and `templatize` lowers through
        # `ast.parse`, which raises `IndentationError` on a nested def.  `lower_source`
        # then returns no roots, the unit is dropped, and the name reports as having no
        # shared structure — the strongest-looking negative produced by a parse failure.
        # MEASURED: all 7 names in the first scoped run read `0 skeleton(s)`, including
        # 14 `visit_FunctionDef` methods that are obviously structurally similar.
        units = [("%s:%d" % (os.path.relpath(p, _pycodemod_core.ROOT), a),
                  textwrap.dedent(txt))
                 for p, a, _b, txt in source_of(name, sorted({p for p, _l in sites}))]
        if len(units) < min_sites:
            continue
        # ⚑ A TEMPLATIZE FAILURE IS A ROW, NOT A SKIP.  `continue` here drops the name
        # from the census entirely, which reads as "this name has no structural
        # collision" — the same false zero as a swallowed import, one row at a time.
        # A name whose bodies could not be lowered is reported with `holes=None`, so
        # "could not decide" and "decided: no shared skeleton" stay distinguishable
        # from "not present".
        try:
            rep = _ir.templatize(units)
        except Exception as exc:
            rows.append((name, len(units), 0, None,
                         ["⚑ templatize failed: %s" % exc], 0, 0))
            continue
        cl = rep.get("clusters") or []
        # holes = the SMALLEST varying-slot count over this name's templates; a name
        # with one 0-hole cluster IS a lift regardless of what its other sites do.
        holes = min([c["holes"] for c in cl], default=None)
        # ⚑⚑ THE STRICT KEY ALONE PRODUCES A FALSE NEGATIVE, AND IT PRODUCED ONE HERE.
        # `full_skeleton` is pre-order DFS over EVERY child and, by its own docstring,
        # "sees the operator" — so two `main`s that both parse-args → dispatch → exit
        # score as DISTINCT skeletons merely because they call different functions.  I
        # read `0/202 shared` off that key and reported "no lift at all, 202 distinct
        # entry points" (operator: *"A convention name is a named pattern.  I find it
        # hard to believe there's nothing liftable or structurally common"*).  That was
        # a fact about the DISCRIMINATOR reported as a fact about the corpus — the same
        # method-vs-substrate error this toolkit files against, committed by the very
        # mode built to stop it.
        #
        # ⚑ AND THE COARSE RUNG WAS ALREADY THERE, one screen from the strict one.
        # `jea_pyalg` grades the SAME interned trace: `head_spine` folds the wedge
        # quotient chain (heads only, children dropped), `full_skeleton` walks
        # everything.  `a = recon quot base rem` is the wedge, and the two readouts are
        # two depths on one curve.  Reporting a single point on a graded family as THE
        # answer is the collapse; both columns ship, and DISAGREEMENT between them is
        # the informative row — shared shape, divergent detail, i.e. parameterisable.
        spines = {}
        for label, src in units:
            try:
                I = _pyalg.Intern()
                roots = _pyalg.lower_source(src, I)
                if not roots:
                    continue
                D = _pyalg.PyDivStr(I)
                spines.setdefault(_pyalg.head_spine(D.trace(roots[0])), []).append(label)
            except Exception:
                continue
        nspine = len(spines)
        spine_shared = sum(len(v) for v in spines.values() if len(v) >= 2)
        rows.append((name, len(units), rep.get("n_skeletons", 0), holes,
                     [m for c in cl for m in c["labels"]], nspine, spine_shared))
    # the graded curve: breadth bands, exactly synth_apex's cut over its member set.
    hi = max(3, (max([r[1] for r in rows], default=0)) // 2)
    bands = {"universal": [], "broad": [], "pairwise": []}
    for r in rows:
        n = r[1]
        bands["universal" if n >= hi else ("broad" if n >= 3 else "pairwise")].append(r)
    for b in bands:
        # a 0-hole (identical) candidate outranks a many-hole one at equal breadth;
        # `None` (no >=2 cluster shares a skeleton at all) sorts last, not first.
        # ⚑ RANK BY SHARING AT EITHER DEPTH, not by site count.  Sorting on `nsites`
        # alone put `main` (202 sites, nothing shared deeply) above `check` (78 sites,
        # 66 shared) — the loudest row, not the most liftable one.
        bands[b].sort(key=lambda r: (-(max(len(r[4]), r[6])), -r[1],
                                     10 ** 6 if r[3] is None else r[3]))
    return [(b, bands[b]) for b in ("universal", "broad", "pairwise") if bands[b]]


def rivals(name, paths=None):
    """Does each `def <name>` REIMPLEMENT, or merely DELEGATE?

    ⚑ BUILT BECAUSE T12's WITNESS COUNTS SHAPE, NOT DIVERGENCE.  T12 is "5
    files still define their own `agda_files`", and `--calls agda_files`
    reports `4 def(s)` — which reads as four rival enumerators.  Opening them,
    all four are ONE-LINE WRAPPERS around `agda_lex.agda_files`, differing
    only in which root they bind.  The convergence the item exists to force
    has already happened; what the census sees is the `def` keyword.

    ⚑ AND "A SHARED NAME IS NOT A SHARED AUTHORITY" HAS A CONVERSE THIS ARC
    HAD NOT NAMED: a duplicated NAME is not a duplicated BODY.  The original
    defect was four different bodies under one name — real divergence,
    correctly found.  Counting `def` sites finds that AND its repair, and
    cannot tell them apart, so the item can never read as done.

    A def is DELEGATING when its body is a single return whose value is a call
    — the thing every one of these four is.  Anything else is REIMPLEMENTING
    and is the population the item actually wants.

    ⚑ DELIBERATELY SYNTACTIC, AND THE LIMIT IS STATED.  This does not check
    that the callee IS the authority: `return _helper(x)` delegates to
    whatever `_helper` names, and resolving that is the scope-aware question
    filed as T20.  So a row saying DELEGATES means "this def adds no body of
    its own", not "this def is correct" — the operator reads the callee.  A
    guess about the callee would be the judgement-not-in-code this exists to
    remove."""
    if cst is None:
        return []
    # ⚑ SAME CONVERSION AS `attr_reads`, and it is the same 93%-is-position-
    # resolution cost: 34s of a 150s `--order` run.  One shared `_per_file`
    # rather than two pool call sites — the vehicle choice is measured once.
    return sorted(_pycodemod_core._per_file(functools.partial(_rivals_one, name),
                            paths if paths is not None else _pycodemod_core.py_files()))


def _rivals_one(name, path):
    """One file's `def <name>` verdicts — the poolable unit."""
    if cst is None:
        return []
    out = []
    try:
        src = open(path, encoding="utf-8").read()
        if "def " + name not in src:
            return []
        mod = cst.parse_module(src)
        wrapper = cst.metadata.MetadataWrapper(mod)
        pos = wrapper.resolve(cst.metadata.PositionProvider)
    except Exception:
        return []
    class V(cst.CSTVisitor):
        METADATA_DEPENDENCIES = (cst.metadata.PositionProvider,)

        def visit_FunctionDef(self, node):
            if node.name.value != name:
                return True
            # the body minus its docstring — a docstring is prose, and
            # counting it as an implementation is how a wrapper reads dense
            stmts = [s for s in node.body.body
                     if not (isinstance(s, cst.SimpleStatementLine)
                             and len(s.body) == 1
                             and isinstance(s.body[0], cst.Expr)
                             and isinstance(s.body[0].value,
                                            cst.SimpleString))]
            verdict, callee = "REIMPLEMENTS", ""
            if len(stmts) == 1 and isinstance(stmts[0], cst.SimpleStatementLine) \
                    and len(stmts[0].body) == 1 \
                    and isinstance(stmts[0].body[0], cst.Return) \
                    and isinstance(stmts[0].body[0].value, cst.Call):
                verdict = "DELEGATES"
                try:
                    callee = mod.code_for_node(
                        stmts[0].body[0].value.func).strip()
                except Exception:
                    callee = "?"
            out.append((path, pos[node].start.line, verdict, callee,
                        len(stmts)))
            return True

    wrapper.visit(V())
    return out


def attr_reads(name, paths=None):
    """Every `.name` ATTRIBUTE ACCESS — the query a FIELD RENAME needs.

    ⚑ BUILT BECAUSE `--binding` RETURNED 0 ON A LIVE FIELD.  Renaming a
    `namedtuple` field (`Row.waiting` -> `Row.graded`), I asked `--binding
    waiting` and got `0 binding(s)` — correct and useless: `r.waiting` BINDS
    nothing, it READS an attribute, so every consumer of the renamed field was
    structurally invisible to the only query that could have found them.  The
    fallback is `grep waiting`, which returns the docstrings and the ⚑ comments
    and hides the four real call sites among them.

    This is the same class the module docstring records for Agda: a shared NAME
    is not a shared authority, and a name in prose is not a use.  A `namedtuple`
    field is exactly a name whose uses are attribute reads and whose prose
    mentions are dense — the worst case for a text scan and a one-line question
    for the CST.

    ⚑ DELIBERATELY UNRESOLVED, AND THE LIMIT IS STATED RATHER THAN HIDDEN.  This
    matches `.name` on ANY receiver, not just the type you are renaming — the
    same bare-name imprecision `--discards` records (T20).  For a distinctive
    field name that is exact; for a common one (`.value`, `.name`) it
    over-reports, and the row's CONTEXT column is what lets a reader discard the
    misses.  A scope-aware resolver would fix both at once; until then the
    honest move is to report the over-approximation WITH its context, never to
    filter by a guess about the receiver."""
    if cst is None:
        return []
    # ⚑ ROUTED THROUGH `_per_file` — the loop was serial and this mode is 33s of a
    # 150s `--order` run, essentially all of it `MetadataWrapper.resolve`.  The
    # worker is a module-level partial because a closure cannot be pickled across
    # a process boundary, and it RETURNS rows rather than appending to an enclosing
    # list for the same reason: shared mutable state does not survive the crossing.
    return sorted(_pycodemod_core._per_file(functools.partial(_attr_reads_one, name),
                            paths if paths is not None else _pycodemod_core.py_files()))


def _attr_reads_one(name, path):
    """One file's `.name` attribute reads — the poolable unit."""
    if cst is None:
        return []
    recv = name[:-2] if name.endswith(".*") else None
    try:
        src = open(path, encoding="utf-8").read()
        # the cheap reject must key on what we are about to look for: `Recv.` for the
        # receiver-scoped form, `.leaf` for the leaf form.
        if (recv + "." if recv else "." + name) not in src:
            return []
        mod = cst.parse_module(src)
        wrapper = cst.metadata.MetadataWrapper(mod)
        pos = wrapper.resolve(cst.metadata.PositionProvider)
    except Exception:
        return []
    found = []

    class V(cst.CSTVisitor):
        METADATA_DEPENDENCIES = (cst.metadata.PositionProvider,)

        def __init__(self):
            self.ctx = ["<module>"]

        def visit_FunctionDef(self, node):
            self.ctx.append(node.name.value)

        def leave_FunctionDef(self, node):
            self.ctx.pop()

        def visit_Attribute(self, node):
            # ⚑ RECEIVER-SCOPED FORM `--attr Recv.*`.  The mode docstring above declares
            # receiver-blindness as deliberate ("never filter by a GUESS about the
            # receiver") — and that is right for `--attr leaf`, where the receiver is an
            # arbitrary expression.  But `Recv.*` asks the INVERSE question, which is not
            # a guess: the receiver is a bare NAME written literally at the call site, so
            # "which attributes hang off `SF`" is decidable from the CST exactly.  It was
            # missing, and its absence is what made "what does a whole-module consumer
            # (`import scope_fix as SF`) actually reach for" unanswerable except by grep —
            # the toolkit gap read as a licence for a textual fallback.
            if recv is not None:
                if isinstance(node.value, cst.Name) and node.value.value == recv:
                    found.append((path, pos[node].start.line,
                                  "%s.%s" % (recv, node.attr.value)))
            elif node.attr.value == name:
                found.append((path, pos[node].start.line, self.ctx[-1]))

    wrapper.visit(V())
    return found


def source_of(name, paths=None):
    """[(path, line, endline, text)] — the SOURCE of every def/class named `name`.

    ⚑ EVERY MODE ANSWERED "WHERE", NONE ANSWERED "WHAT DOES IT SAY".  Reading a
    reference implementation inside `--archive` (whose tree is a temp dir removed
    on exit, so there is no path to `Read` afterwards), `--calls compute` located
    `routing.py:58` and there was no way to see the body.  The only routes left
    were the ones this file forbids — extract by hand, or `sed -n '58,90p'`.

    ⚑ AND THIS IS NOT THE DELETED `--show` COMING BACK.  That was a bolt-on on
    `archive_defs`, a SECOND walker for the archive alone; the finding recorded
    at its deletion was that an archive is a SCOPE, not a question.  This is the
    other half of that lesson: a corpus-shaped READ is a QUESTION, so it belongs
    in `_dispatch` where every scope (`--in`, `--archive`, `--package`) gets it
    at once, rather than in the envelope where only one would.

    Extents come from the CST, not a line count — a def ends where its body ends,
    which a fixed window gets wrong in both directions (truncating a long
    function, swallowing the next one after a short).
    """
    if cst is None:
        return []
    out = []
    for path in list(paths or _pycodemod_core.py_files()):
        try:
            src = open(path, encoding="utf-8").read()
            if name not in src:            # cheap reject; the CST decides
                continue
            lines = src.splitlines()
            mod = cst.parse_module(src)
            wrapper = cst.metadata.MetadataWrapper(mod)
            pos = wrapper.resolve(cst.metadata.PositionProvider)
        except Exception:
            continue

        class V(cst.CSTVisitor):
            METADATA_DEPENDENCIES = (cst.metadata.PositionProvider,)

            def _emit(self, node):
                if node.name.value != name:
                    return
                a, b = pos[node].start.line, pos[node].end.line
                out.append((path, a, b, "\n".join(lines[a - 1:b])))

            def visit_FunctionDef(self, node):
                self._emit(node)

            def visit_ClassDef(self, node):
                self._emit(node)

        wrapper.visit(V())
    return sorted(out)


def key_reads(key, paths=None):
    """Every read of the STRING KEY `key` — `d["k"]`, `d.get("k")`, `d.get("k", x)`,
    `"k" in d`, `d.setdefault("k")`, `d.pop("k")` — plus where it is DECLARED as a
    literal in a collection (the schema site).

    ⚑ BUILT BECAUSE `--attr` RETURNED 0 ON A LIVE FIELD, one layer down from the
    reason `--attr` itself was built.  Asking which code reads paperkit's `_src`
    provenance field, `--attr _src` reported `0 attribute read(s)` — correct and
    useless, because paperkit's whole data model is DICTS: `parse()` returns
    `{key: {field: value}}` and every consumer writes `f["_src"]`, not `f._src`.
    A record whose fields are string keys is structurally invisible to BOTH
    `--binding` (a subscript binds nothing) and `--attr` (there is no attribute),
    so the only remaining route was `grep '"_src"'` — which cannot tell a read
    from the docstring paragraph explaining the field, and this file exists
    because that distinction is the whole point.

    ⚑ THE SCHEMA SITE IS A DISTINCT KIND, NOT A READ.  `_SCALAR = ("title", ...,
    "link")` DECLARES the field set; `f["link"]` USES it.  Folding them together
    reproduces the `ref`-vs-`call` collapse `--dead` already paid for: the
    declaration would make every field look used and the census would go quiet.
    They are reported as `decl` and `read` so "declared but never read" — a dead
    field, the dict-shaped twin of a dead capability — stays visible.

    ⚑ SAME STATED IMPRECISION AS `--attr`: the receiver is not resolved, so this
    matches the key on ANY dict.  For a distinctive key (`rests-on`, `_src`) that
    is exact; for a common one (`name`, `path`) it over-reports, and the CONTEXT
    column is what lets a reader discard the misses.  Reporting the
    over-approximation with its context is honest; filtering by a guess is not.
    """
    if cst is None:
        return []
    out = []
    _READERS = {"get", "setdefault", "pop", "__contains__"}
    for path in list(paths or _pycodemod_core.py_files()):
        try:
            src = open(path, encoding="utf-8").read()
            if key not in src:             # cheap reject; the CST decides
                continue
            mod = cst.parse_module(src)
            wrapper = cst.metadata.MetadataWrapper(mod)
            pos = wrapper.resolve(cst.metadata.PositionProvider)
        except Exception:
            continue

        def _lit(node):
            """The str value of a plain string literal node, else None."""
            if isinstance(node, cst.SimpleString):
                try:
                    v = ast.literal_eval(node.value)
                except Exception:
                    return None
                return v if isinstance(v, str) else None
            return None

        class V(cst.CSTVisitor):
            METADATA_DEPENDENCIES = (cst.metadata.PositionProvider,)

            def __init__(self):
                self.ctx = ["<module>"]

            def visit_FunctionDef(self, node):
                self.ctx.append(node.name.value)

            def leave_FunctionDef(self, node):
                self.ctx.pop()

            def _hit(self, node, kind):
                out.append((path, pos[node].start.line, kind, self.ctx[-1]))

            # d["k"]  — the subscript read
            def visit_Subscript(self, node):
                for el in node.slice:
                    idx = getattr(el.slice, "value", None)
                    if idx is not None and _lit(idx) == key:
                        self._hit(node, "read")

            # d.get("k") / d.pop("k") / d.setdefault("k")
            def visit_Call(self, node):
                fn = node.func
                if isinstance(fn, cst.Attribute) and fn.attr.value in _READERS:
                    if node.args and _lit(node.args[0].value) == key:
                        self._hit(node, "read")

            # "k" in d
            def visit_Comparison(self, node):
                if _lit(node.left) == key and any(
                        isinstance(c.operator, cst.In) for c in node.comparisons):
                    self._hit(node, "read")

            # a literal in a tuple/list/set collection = the SCHEMA declaration
            def visit_Tuple(self, node):
                self._coll(node)

            def visit_List(self, node):
                self._coll(node)

            def visit_Set(self, node):
                self._coll(node)

            def _coll(self, node):
                for el in node.elements:
                    if _lit(el.value) == key:
                        self._hit(node, "decl")
                        return

        wrapper.visit(V())
    return sorted(out)


def literal_sites(text, paths=None):
    """[(path, line, role, ctx, value)] — every STRING LITERAL whose VALUE contains
    `text`, classified by the ROLE the literal plays.

    role='compare'  the literal is an operand of a comparison — `back == "sqlite"`,
                    `kind in ("sqlite", "postgres")`.  THE DISPATCH SITES: these are
                    the branches a value's retirement deletes.
    role='arg'      passed to a call — `dialect("sqlite")`, `ph(1, "sqlite")`.  The
                    CALLERS that name the value; each one is a decision to migrate.
    role='decl'     an element of a tuple/list/set/dict literal — the ROSTER site.
    role='other'    an assignment RHS, a default, a return, an f-string part.
    role='doc'      inside a docstring.

    ⚑ BUILT BECAUSE `--key` ANSWERS THE MIRROR QUESTION AND WAS THE ONLY NEIGHBOUR.
    `--key "sqlite"` asks where a string is used as a dict KEY; the question a
    backend retirement asks is where it is used as a VALUE, and no mode had it.  The
    fallback was `grep sqlite`, which the structural-query hook correctly refuses —
    and would be wrong even if allowed: measured over `jea/` + `scripts/`, the token
    appears in far more ⚑ COMMENT lines (explaining the defect class the branch
    exists for) than in code, so a grep census reports the documentation as the work.
    A comment is not a literal, so it is excluded here BY CONSTRUCTION rather than by
    a filter — the same distinction `--calls` draws when it refuses to count a name
    in a docstring as a call.

    ⚑ AND `doc` IS A ROLE RATHER THAN AN EXCLUSION, WHICH IS THE OTHER HALF. A
    docstring IS a string literal, so dropping it silently would make this mode
    disagree with `--commentary` about the same file.  Reported and ranked LAST: a
    retirement must still update the prose, but a prose mention never blocks the
    code change, and collapsing the two is how "0 sites left" gets claimed with the
    module docstring still describing the removed branch.

    ⚑ SUBSTRING, CASE-SENSITIVE, AND UNRESOLVED — stated rather than hidden. It
    matches `"sqlite"` inside `"sqlite3"` and inside `"sqlite:///"`, which is
    correct for a retirement sweep (all three are the same migration) and
    over-reports for a narrow question.  The VALUE column is what lets a reader
    discard the misses; filtering by a guess is what this repo already paid for.
    """
    if cst is None:
        return []
    out = []

    def _strs_under(node, acc):
        """Every SimpleString id in `node`'s subtree — a docstring may be an
        implicit CONCATENATION, whose parts are the nodes this mode matches."""
        class _S(cst.CSTVisitor):
            def visit_SimpleString(self, n):
                acc.add(id(n))
        node.visit(_S())

    for path in list(paths or _pycodemod_core.py_files()):
        try:
            src = open(path, encoding="utf-8").read()
            if text not in src:            # cheap reject; the CST decides
                continue
            wrapper = cst.metadata.MetadataWrapper(cst.parse_module(src))
            pos = wrapper.resolve(cst.metadata.PositionProvider)
            par = wrapper.resolve(cst.metadata.ParentNodeProvider)
        except Exception:
            continue

        # ⚑ THE DOCSTRING SET IS BUILT FROM `wrapper.module`, NOT THE PARSED MODULE.
        # `MetadataWrapper` DEEP-COPIES its input by default, so node identity in the
        # tree the visitor walks does not match the tree `parse_module` returned —
        # ids collected from the original would match nothing and every docstring
        # would report as `other`.  Measured by the case below, not by review.
        docs = set()

        class _D(cst.CSTVisitor):
            def _first(self, node):
                body = getattr(node, "body", None)
                body = getattr(body, "body", body)      # IndentedBlock → its body
                if not body:
                    return
                st = body[0]
                if isinstance(st, cst.SimpleStatementLine) and st.body:
                    e = st.body[0]
                    if isinstance(e, cst.Expr) and isinstance(
                            e.value, (cst.SimpleString, cst.ConcatenatedString)):
                        _strs_under(e.value, docs)

            visit_Module = _first
            visit_FunctionDef = _first
            visit_ClassDef = _first

        wrapper.module.visit(_D())

        class V(cst.CSTVisitor):
            METADATA_DEPENDENCIES = (cst.metadata.PositionProvider,
                                     cst.metadata.ParentNodeProvider)

            def __init__(self):
                self.ctx = ["<module>"]

            def visit_FunctionDef(self, node):
                self.ctx.append(node.name.value)

            def leave_FunctionDef(self, node):
                self.ctx.pop()

            def visit_SimpleString(self, node):
                try:
                    v = ast.literal_eval(node.value)
                except Exception:
                    return
                if not isinstance(v, str) or text not in v:
                    return
                out.append((path, pos[node].start.line, self._role(node),
                            self.ctx[-1], v))

            def _role(self, node):
                if id(node) in docs:
                    return "doc"
                # ⚑ THE WALK STOPS AT THE STATEMENT, and the bound is load-bearing
                # rather than a performance guess: without it, every literal anywhere
                # inside a function called from a comparison would climb out of its
                # own statement and report as `compare`.  A role is a fact about the
                # EXPRESSION the literal sits in, so the enclosing statement is where
                # the question stops being askable.
                cur = node
                for _ in range(12):
                    try:
                        cur = par[cur]
                    except Exception:
                        return "other"
                    if isinstance(cur, cst.Comparison):
                        return "compare"
                    if isinstance(cur, cst.Arg):
                        return "arg"
                    if isinstance(cur, (cst.Tuple, cst.List, cst.Set, cst.Dict)):
                        return "decl"
                    if isinstance(cur, (cst.SimpleStatementLine, cst.BaseCompoundStatement,
                                        cst.Module)):
                        return "other"
                return "other"

        wrapper.visit(V())
    return sorted(out)


def dead(paths=None):
    """[(path, name, line)] — defs never called anywhere in the corpus.

    Excludes `_selftest`/`main`/dunders and anything CLI-dispatched, which are
    entry points by design rather than dead code.

    ⚑ SCOPING THIS TO A SUBSET IS A TRAP, AND IT FIRED ON ME.  The verdict is
    "no caller **in the scanned population**", so `--dead scripts/ratchet.py`
    reports `set_ratchet` and `check_argv` as dead — they have TEN and FOUR
    cross-file callers respectively, none of which were scanned.  A scoped run
    answers a scoped question (§51's rule, here on a read rather than a write):
    for a DEAD-CAPABILITY verdict the population must be the whole corpus, which
    is why `paths=None` is the default.  The CLI says so at the point of use.

    ⚑ AND A USE-AS-VALUE IS A USE.  This counted only `call` rows, so a function
    handed to something else rather than invoked — an OTLP observable-gauge
    `callbacks=[cb]`, a decorator target, a registry entry, `key=fn`, `return inner`
    — reported as DEAD while being live.  Measured on `scripts/membudget_otlp.py`,
    where `cb` (:116, returned from a factory) and `hb_cb` (:131, passed as
    `callbacks=[hb_cb]`) were both named by `--dead` before the `ref` kind existed.
    A false positive in a query you ACT on is a bug and not a caveat, because the
    action `--dead` invites is deletion.
    """
    rows = scan(paths)
    called = {n for _p, k, n, _l in rows if k in ("call", "ref")}
    out = []
    for p, k, n, l in rows:
        if k != "def" or n in called:
            continue
        if n.startswith("__") or n in ("main", "_selftest"):
            continue
        # a name mentioned in an `if "--flag"` dispatch is reachable from the CLI
        if f'"{n}"' in open(p, encoding="utf-8").read():
            continue
        if framework_dispatch(n):
            continue
        out.append((p, n, l))
    return out


# ⚑⚑ THE CALLER IS OUTSIDE THE CORPUS, WHICH IS NOT THE SAME AS ABSENT.  Each of
# these prefixes is a NAMING CONTRACT with a framework that invokes the def by
# constructing its name: libcst calls `visit_<NodeType>`/`leave_<NodeType>` off the
# node class, Textual resolves `action_<name>` from a `Binding` table's string and
# `on_<message>` from the message class, pytest collects `test_*` by prefix.  The
# def is reached; the call site is in a library this census does not scan.
#
# ⚑ MEASURED 2026-08-18, AND `pycodemod` WAS ITS OWN WORST CASE: `--dead` named
# `visit_Call`, `visit_Name`, `leave_FunctionDef` and `visit_FunctionDef_name` —
# the visitor methods THIS FILE dispatches every query through — while the tool
# was being used to decide what to delete.  A census that cannot see the framework
# that calls it reports its own engine as removable.
#
# ⚑ A PREFIX TABLE AND NOT A NAME LIST, because a name list is the frozen-roster
# defect (`run_selftests.py:38-48` records three recurrences): a new `visit_Return`
# or `action_quit` must be covered the day it is written, without editing this file.
# The rule is the CONTRACT, not its current instances.
FRAMEWORK_PREFIXES = {
    "visit_": "libcst/ast visitor — dispatched off the node type",
    "leave_": "libcst visitor — dispatched off the node type",
    "action_": "Textual — resolved from a Binding table string",
    "on_": "Textual — resolved from the message class name",
    "test_": "pytest — collected by prefix",
}


def framework_dispatch(name):
    """The framework naming-contract a def satisfies, or None.

    ⚑ RETURNS THE CONTRACT, NOT A BOOLEAN, so a caller can SAY why it exempted a
    def.  An exemption an operator cannot see the reason for is indistinguishable
    from a census that silently misses things, and this table exists precisely
    because a silent miss invited a deletion.
    """
    for pre, why in FRAMEWORK_PREFIXES.items():
        if name.startswith(pre) and len(name) > len(pre):
            return why
    return None


def bindings(name, path):
    """[(kind, qualname, line, scope_start, scope_end)] — where `name` is BOUND.

    ⚑ BUILT BECAUSE I HAND-ROLLED IT TWICE IN ONE TURN (user: "no greps, no
    seds, no test-think-test-think").  Placing two selftest cases, I needed to
    know where a local `grouped` was assigned and which suite lines were inside
    its scope.  I answered with `grep -n "grouped = ties"` and a `Read` at an
    offset, then edited, reran, misplaced them, and repeated — four cycles for
    a question with one structural answer.  The failure was not the grep; it
    was that "where is this name bound, and where is it live?" had no home,
    so every future reader re-derives it the same way.

    ⚑ AND IT IS THE `--calls` QUESTION'S MISSING HALF.  `--calls` answers "is
    this capability reached"; this answers "is this name AVAILABLE here" — the
    Python twin of `agda_lex.binds_at`, which this repo built for exactly the
    same reason after a file-level scope test could not tell a top-level use
    from one inside a telescope (plan §11d).  A bare name is not a decidable
    unit in either language.

    Assignment, augmented assignment, `for`, `with ... as`, comprehension
    targets, parameters, imports and defs all BIND; a read does not."""
    try:
        src = open(path, encoding="utf-8").read()
    except OSError as e:
        return [("<unreadable>", str(e), 0, 0, 0)]
    try:
        tree = ast.parse(src, filename=str(path))
    except SyntaxError as e:
        # ⚑ A PARSE FAILURE IS A VERDICT, NOT A CRASH — the same rule
        # `roundtrip` follows, so a broken file reports rather than aborting a
        # sweep over its siblings.
        return [("<syntax-error>", str(e), 0, 0, 0)]

    out = []

    def scope_of(node):
        return (getattr(node, "lineno", 0),
                getattr(node, "end_lineno", 0) or getattr(node, "lineno", 0))

    def walk(node, prefix, scope):
        for child in ast.iter_child_nodes(node):
            here = prefix
            sc = scope
            if isinstance(child, (ast.FunctionDef, ast.AsyncFunctionDef,
                                  ast.ClassDef, ast.Lambda)):
                nm = getattr(child, "name", "<lambda>")
                if nm == name:
                    out.append(("def", prefix + nm, child.lineno, *scope_of(child)))
                here = prefix + nm + "."
                sc = scope_of(child)
                # ⚑ NO EXPLICIT `args.args` LOOP: the recursion reaches every
                # `ast.arg` node anyway, so scanning them here recorded each
                # parameter TWICE.  Caught by the selftest, which is the point —
                # a double-counted binding would inflate every census built on
                # this, and the count is what a caller trusts.
                pass
            elif isinstance(child, ast.Name) and isinstance(child.ctx, ast.Store):
                if child.id == name:
                    out.append(("assign", prefix + child.id, child.lineno, *scope))
            elif isinstance(child, (ast.Import, ast.ImportFrom)):
                for al in child.names:
                    if (al.asname or al.name.split(".")[0]) == name:
                        out.append(("import", prefix + name, child.lineno, *scope))
            elif isinstance(child, ast.arg) and child.arg == name:
                out.append(("param", prefix + child.arg, child.lineno, *scope))
            walk(child, here, sc)

    walk(tree, "", (1, len(src.splitlines())))
    return out


def _print_bindings(name, paths):
    files = _pycodemod_core.py_files(*paths) if paths else _pycodemod_core.py_files()
    total, shown = 0, 0
    for p in files:
        rows = bindings(name, p)
        if not rows:
            continue
        total += len(rows)
        shown += 1
        rel = os.path.relpath(p, _pycodemod_core.ROOT)
        for kind, qual, line, lo, hi in rows:
            print(f"  {kind:<7} {rel}:{line}  {qual}  [live {lo}..{hi}]")
    # ⚑ `n of m`, ALWAYS.  "There are no sweeps, only censuses" — a bare list
    # cannot distinguish "no bindings" from "no files searched", and that is the
    # exact failure this session kept hitting.
    print(f"{name}: {total} binding(s) in {shown} of {len(files)} file(s)")
    return 0




# ⚑⚑⚑ THE PARSED-TREE CACHE IS BOUNDED, AND THE BOUND IS NOT OPTIONAL. Unbounded, it
# held every `MetadataWrapper` for the corpus and the pipeflow suite was OOM-KILLED at
# its 192MB membudget lease — reported as `UNFIT`, i.e. the suite vanished from the run
# rather than failing: 73 suites became 72 and 2872 cases became 2829. I traded 331s for
# memory without measuring the memory, which is the same unmeasured-premise shape as the
# pastel fills two hours earlier.
#
# ⚑⚑ AN LRU AND NOT A BIGGER LEASE. Raising the lease buys the same trade at a higher
# ceiling and moves the wall rather than removing it — `membudget`'s own message names
# both options and says which is debt. A window large enough for the working set of one
# whole-corpus pass keeps the speedup; holding the corpus is what did not fit.
#
# ⚑ SMALLEST-USEFUL, NOT LARGEST-AFFORDABLE: the passes that share trees are the several
# questions asked back-to-back over the SAME file list, so the window need only span one
# file's reuse across those passes, not the corpus.
from collections import OrderedDict as _OD  # noqa: E402
_WRAPPER_CACHE = _OD()
_WRAPPER_CACHE_MAX = int(os.environ.get("PYCODEMOD_TREE_CACHE", "24"))


class KwIndex(dict):
    """`(path, line) -> {keywords}` that CARRIES THE CONTEXT IT WAS GATHERED UNDER.

    ⚑ AN OUT-PARAMETER HAS AN UNCHECKED PRECONDITION, AND THAT IS THE DEFECT
    (user, 2026-08-01: *"a cleaner solution would be to carry kwseen, but require it
    to be validated against an expected context before used, so that it's understood
    what it means in the context in which it's used — dependent typing applied to
    recursive calls"*).

    A bare `dict` filled by `scan()` is a set of keyword facts with its provenance
    stripped: the caller must REMEMBER that this one came from a scan over *these*
    paths for *this* target.  Reading it against a different query is then a silent
    wrong answer — `forwards()` would report a migration as current using keywords
    gathered from an unrelated population.  Module-level state has the same defect
    and merely hides it further.

    So the context is part of the VALUE, not part of the caller's discipline: the
    index is stamped with `(target, population)` at construction, and `.check()`
    REFUSES a read whose expected context differs.  That makes the precondition a
    checkable property of the object rather than an invariant nobody enforces —
    the same move as `tree_stamp()` refusing to bank a census whose tree moved
    (§51), and as the ledger recording WHAT it measured rather than trusting the
    reader to know.  Mismatched context is an ERROR, never a plausible answer.
    """

    def __init__(self, target=None, population=None):
        super().__init__()
        self.target = target
        # frozenset, so ordering never makes two identical populations differ
        self.population = frozenset(population) if population is not None else None
        # ⚑ `(path, line) -> {keyword -> "literal"|"computed"}`, carried HERE and
        # not in a second dict, so the context stamp guards both facts.  The
        # keyword NAMES answer "was it passed"; the shapes answer "was it
        # measured or asserted" — one scan, one stamp, two readings.
        self.shapes = {}
        # ⚑ `(path, line) -> {keyword -> constant | UNKNOWN}` — the third reading,
        # under the same stamp.  NAMED `constants` AND NOT `values`, DELIBERATELY:
        # this class subclasses `dict`, so an attribute spelled `values` would
        # SHADOW `dict.values()` — every consumer that iterates the index would get
        # a dict where it expected a view, and the break would surface far from
        # here.  A name collision with the base class is not a style question.
        self.constants = {}
        # ⚑ `(path, line) -> enclosing def name` — the fourth reading, same stamp.
        self.contexts = {}
        # ⚑ `(path, line) -> {ordinal -> constant | UNKNOWN}` — the FIFTH reading,
        # under the same stamp for the same reason as the other four: a second bare
        # dict would put the provenance back in the caller's memory, which is the
        # unchecked precondition this class exists to remove.  Positional, because
        # the four readings above are keyword-only and therefore cannot see the call
        # shape that writes this store.
        self.positions = {}
        # ⚑ `(path, line) -> {ordinal -> the argument's SOURCE TEXT}` — the SEVENTH
        # reading, same stamp, same reason as the six around it.  `positions` above
        # carries what an argument EVALUATES to and returns UNKNOWN for every bare
        # name; this carries what the author WROTE there.  Both are needed at once by
        # any consumer that must POINT AT a call: a write-mode open is RECOGNISED by
        # `positions[1] == "w"` and LOCATED by `possrc[0] == "path"`, and neither
        # reading alone answers "which variable does this site write".
        #
        # ⚑⚑⚑ AND THE SPELLING OF THIS VERY COMMENT IS THE ARGUMENT FOR THE READING.
        # An earlier draft wrote the call out literally, and `check_snapshot_guard`'s
        # TEXTUAL `WRITE_VAR` regex matched the PROSE — censusing this module as an
        # in-place editor and breaking a frozen-at-0 ratchet. The comment explaining
        # why a locator must be structural was itself mis-located by the textual one.
        self.possrc = {}
        # ⚑ `(path, line) -> the call's RECEIVER` (`os` in `os.replace(...)`), None for
        # a bare call — the EIGHTH reading, same stamp, same reason.  `_Scan` has
        # recorded this since the dotted-target work, but only INSIDE the visitor,
        # where it serves `scan`'s own `recv_want` filter and is then discarded.  A
        # consumer that must partition calls by receiver across a WHOLE-CORPUS scan
        # (`target=None`, where `recv_want` cannot apply) therefore had the fact
        # computed and thrown away, and had to re-derive it from source text — which is
        # the grep defect this module exists to avoid, on the one axis that separates
        # `os.replace` (a filesystem rename) from `s.replace` (a string substitution).
        self.receivers = {}
        # ⚑⚑ `(path, line) -> [enclosing `if` tests, outermost first]` — the SIXTH
        # reading, same stamp, same reason.  The five above answer questions about a
        # call's ARGUMENTS; this one answers where the call SITS, which is a different
        # axis and the one that hid a real defect: `edit_snapshot.guard` — the
        # mutation-intent gate — is called at 61 sites, and at `drop_dead_renames.py:143`
        # it sits under `if apply:`.  So the guard that exists to force an operator to
        # STATE intent runs only once intent has already been stated as apply, and the
        # UNSTATED case (the entire population the ratchet measures) is the one branch it
        # can never reach.  `--calls` reported that site as present and gave no way to
        # see it, so the census read as adopted while being structurally blind.
        #
        # ⚑ A GUARD BEHIND THE DECISION IT GATES IS A WRITE GUARD, NOT A DECISION GUARD,
        # and no amount of paydown fixes it — the census reads clean forever because the
        # default-dry path never reaches the guard at all.
        self.conds = {}

    def check(self, target, population):
        """Refuse to be read under a context other than the one gathered."""
        want = frozenset(population) if population is not None else None
        if self.target != target or self.population != want:
            raise ValueError(
                f"KwIndex context mismatch: gathered for target={self.target!r} "
                f"over {len(self.population or ())} file(s), read for "
                f"target={target!r} over {len(want or ())} file(s). "
                f"A keyword index is only meaningful for the query that produced it."
            )
        return self
