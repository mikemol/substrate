#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Mike Mol
"""COMPUTE what a `.pyi` would need to state, by recursive dataflow over the corpus.

⚑⚑⚑ THIS LIFTS `iface_infer`'s FLOOR, AND THAT FLOOR WAS STATED TOO WIDELY. That module
records *"inference PROPAGATES the types a source states; it does not MANUFACTURE types the
source never stated"* — true of a RETURN, false of a PARAMETER. A return type is a fact
about the callee's body. A parameter type is not a fact about the callee at all: it is
determined by what CALL SITES pass in and what the BODY requires of it, and both live
elsewhere in the corpus, one hop away. `def scan_file(path)` is not an absence of
information — four call sites pass it, and every one of them says something.

⚑⚑ SO THE DIRECTION OF THE READ IS THE WHOLE DESIGN. `iface_infer` reads a def and asks
"what does this STATE". This reads a SLOT and asks "what does the corpus KNOW", which is a
query over incoming edges (arguments at call sites) and outgoing ones (uses in the body).
The answer is a JOIN of witnesses, each carrying a `file:line` — never a bare type string.
A computed type with no witness is exactly the authored claim this arc exists to stop.

⚑⚑⚑ TERMINATION. The recursion is over a finite graph whose nodes are slots
(`module.func#param`) and it bottoms out only on GIVEN types, never inferred ones. The
bottoming-out set is `iface_bottom` — B1 literals, B3 typed surfaces, B4 body requirements
— plus B2, a slot the source already annotates, read through `iface_infer`. Because
`iface_bottom.given_type` cannot recurse, every path either reaches it, reaches an
annotation, or is REPORTED unresolved. Cycles (mutual recursion; a parameter passed through
to a parameter passed back) are caught by an in-progress set and named as `CYCLE`.

⚑⚑ A SLOT THAT DOES NOT BOTTOM OUT IS THE FINDING, NOT A FAILURE. It says one of several
things and all of them are worth knowing. Writing `Any` there would convert a precise
negative result into a false positive.

⚑⚑⚑ AND "NOT REACHED" IS NOT ONE FINDING — IT WAS THREE, PRINTED AS ONE SENTENCE. Until
`unreached_kind` was split out, a slot no argument reached reported *"the slot is DEAD or
reached only dynamically"*: a disjunction offered to the reader with no way to settle it,
which is `report-presence-never-absence` committed inside the reader built to carry
witnesses. `DEFAULTED`, `UNCALLED` and `OMITTED` are now separate statuses with separate
evidence and opposite instructions — one is not dead at all, one is a fact about the corpus
boundary, and one is a live latent `TypeError`. See `unreached_kind`.

⚑⚑ WHAT WAS REUSED, AND WHAT THAT DELETED FROM THIS FILE. `corpus.py_files` is the
population; `iface_infer` owns B2, so there is no second annotation walk; `iface_bottom`
owns the floor. No call-graph builder is written here — `pycodemod --calls <name>` already
indexes the corpus, and this walk asks the same question of the same trees.

⚑⚑⚑ MYPY DOES NOT ANSWER THIS, AND `--sites` IS THE MEASUREMENT RATHER THAN THE OPINION.
`--disallow-any-expr` over an unannotated module emits hundreds of findings, every one of
the form *"Expression has type Any"* or *"Call to untyped function in typed context"*. That
is a FORWARD PROPAGATION TRACE — it names each site where `Any` ARRIVED and which
unannotated def emitted it, which is genuinely useful and is why the mode exists. But it
runs in the wrong direction for this question. Mypy types a call `scan_file(p)` by reading
the parameter's DECLARATION; with none, it writes `Any` and moves on. It never asks what `p`
was, because nothing in a checker's job requires it to. The information the operator
identified is real and present in the corpus; mypy simply is not the reader of it.

Usage: iface_dataflow.py --module <path> | --slot <path> <func> [param]
       iface_dataflow.py --sites <path> | --selftest
"""

from __future__ import annotations

import ast
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path

from substrate import corpus, iface_bottom, iface_infer
from substrate.iface_bottom import Witness

# A slot key is `<module>.<func>#<param>`; the return slot spells the param `<return>`.
RETURN_SLOT = "<return>"

# `--slot` takes a path and a function, and optionally a parameter.
_SLOT_MIN_OPERANDS = 2

# How many witnesses to print per slot before eliding — the rest are in the data.
_SHOWN_WITNESSES = 6

# How many mypy findings `--sites` prints before eliding.
_SHOWN_SITES = 40

# How much of a default expression the DEFAULTED note quotes before eliding.
_SHOWN_DEFAULT = 40

# ⚑ THE STATUSES THAT MEAN "A TYPE WAS DETERMINED". Named once because three readers ask it
# (`Computed.computed`, the renderer's partition, the selftest) and a fourth spelling is how
# a status silently stops counting as an answer.
#
# ⚑⚑⚑ `FIXTURE` IS DELIBERATELY *NOT* IN HERE, AND THAT IS THE WHOLE OF Ⓝ104f. A slot whose
# only evidence is a test fixture HAS a well-formed type with a `file:line` behind it — which
# is precisely why it must not read COMPUTED. See `PROVENANCE` and `_provenance_verdict`.
RESOLVED = ("COMPUTED", "STATED")

# ⚑⚑ THE STATUSES THAT MEAN "NO ARGUMENT REACHED THIS SLOT", each a DIFFERENT fact — see
# `unreached_kind`. They are grouped for the renderer, which must still print them apart:
# grouping them for LAYOUT is the opposite of collapsing them into one verdict, and this
# tuple exists so a new kind cannot be added without the renderer learning about it.
UNREACHED = ("DEFAULTED", "UNCALLED", "OMITTED")

# Every status a slot can carry that is not a type. `CYCLE` and `UNRESOLVED` are blocked
# UPSTREAM (evidence exists but does not bottom out); the `UNREACHED` three are blocked at
# the slot itself.
STUCK = ("UNRESOLVED", "CYCLE", *UNREACHED)

# ⚑⚑⚑ `FIXTURE` IS ITS OWN PARTITION AND BELONGS TO NEITHER OF THE OTHER TWO. It is NOT
# `RESOLVED` — a fixture is not a contract, which is the whole of Ⓝ104f — and it is NOT
# `STUCK` either, because the walk did not fail to reach anything: it reached a well-formed
# type, at a checkable `file:line`, and the finding is WHERE that evidence lives. Folding it
# into `STUCK` would report a fully-witnessed slot as unreached, which is the same
# absence-vs-boundary collapse `unreached_kind` was split to end.
FIXTURE = "FIXTURE"


@dataclass(frozen=True, slots=True)
class Computed:
    """What the corpus determines about one slot, with every witness that determined it.

    ⚑ `status` IS MANY-VALUED FOR A REASON. A slot with agreeing witnesses, a slot with
    DISAGREEING ones, and the several distinct ways a slot can have NONE are all different
    facts; collapsing them to a bool would reproduce the `Any` this module refuses. Only the
    first is a type.
    """

    slot: str
    witnesses: tuple[Witness, ...]
    status: str
    note: str = ""

    @property
    def types(self) -> tuple[str, ...]:
        """Return the distinct types the witnesses claim, sorted."""
        return tuple(sorted({w.type_name for w in self.witnesses}))

    @property
    def computed(self) -> str | None:
        """Return the single computed type, or None when there is not exactly one.

        ⚑ A JOIN OF DISAGREEING WITNESSES IS NOT A TYPE. Two witnesses saying `str` and
        `Path` mean either a union or a wrong call site, and this reader cannot tell which
        — so it reports both rather than picking. Picking is what an authored stub does,
        and that is the defect class the whole arc is about.

        ⚑⚑ AND AN UNRESOLVED SLOT HAS NO TYPE EVEN WHEN IT CARRIES WITNESSES. A partially
        resolved return keeps the arms it understood — worth reading — but those witnesses
        are a FRAGMENT, not a join, and a reader reaching for `.computed` must not be
        handed one. The status gates the type; the witnesses stay visible either way.

        ⚑⚑⚑ THE REFINED SPELLING IS THE ANSWER WHEN COARSE WITNESSES ABSTAINED. `_verdict`
        already decided these witnesses agree — a `tuple[Any, ...]` beside a
        `tuple[bool, list[str]]` is one refined reading and one un-refined one, not two
        types. Reporting `None` here because `types` still holds both SPELLINGS would throw
        away the very refinement that made the slot resolvable, and the status would say
        COMPUTED while the type came back empty. The abstention rule has to hold in both
        places or it holds in neither.
        """
        if self.status not in RESOLVED:
            return None
        t = self.types
        if len(t) == 1:
            return t[0]
        refined = [n for n in t if n not in _COARSE]
        # ⚑⚑⚑ THE ABSTENTION MUST RE-CHECK THE CONSTRUCTOR HERE, AND THE UNION RULE IS WHAT
        # MADE THE MISSING CHECK REACHABLE. `_verdict` guards its abstention with
        # `_consistent`; this property did not, and while every multi-type slot was a CONFLICT
        # that gap was unreachable — `.computed` returns None on a CONFLICT before it can
        # matter. The moment a return with several types became COMPUTED, `list[str]` beside
        # `tuple[Any, ...]` reached this line and reported a confident `list[str]`, silently
        # DISCARDING the tuple arm. Two readers of one rule, and the second was the wrong one.
        if len(refined) == 1 and _consistent(refined[0], set(t)):
            return refined[0]
        # ⚑⚑ Ⓝ104g — A RESOLVED RETURN WITH SEVERAL TYPES IS A UNION, AND IT REACHES HERE
        # ONLY BECAUSE `_verdict` ALREADY RULED IT ONE. The status is the gate: a parameter
        # that disagreed is CONFLICT and returned None three lines up, so anything still
        # COMPUTED with several types is a return whose arms are alternatives. Spelling it
        # `None` here would say COMPUTED while handing back no type — the same
        # status-says-yes/type-says-nothing split the coarse-abstention note above records.
        return _union(set(t)) if self.slot.endswith(f"#{RETURN_SLOT}") else None


@dataclass(frozen=True, slots=True)
class Module:
    """One parsed corpus module, indexed for the queries the walk makes of it."""

    path: str
    tree: ast.Module
    functions: dict[str, ast.FunctionDef | ast.AsyncFunctionDef]

    @property
    def name(self) -> str:
        """Return the module's bare stem, the way a slot key spells it."""
        return Path(self.path).stem


def from_source(src: str, path: str) -> Module | None:
    """Build a Module from source TEXT — the pure core `load` wraps.

    ⚑ THE SELFTEST MUST NOT NEED A FILE ON DISK. A case that writes a temp file can fail
    for filesystem reasons and be read as a logic failure, which is the least useful kind
    of red suite.
    """
    try:
        tree = ast.parse(src, filename=path)
    except SyntaxError:
        return None
    return Module(
        path,
        tree,
        {n.name: n for n in tree.body if isinstance(n, ast.FunctionDef | ast.AsyncFunctionDef)},
    )


def load(path: str) -> Module | None:
    """Parse one corpus module, or None when it cannot be read or parsed.

    ⚑ UNREADABLE IS `None`, NEVER AN EMPTY MODULE — the same rule `iface_infer.interface_of`
    states. A file the walk could not read and a file with no functions are opposite facts,
    and rendering them alike lets a parse failure enter the report as a clean result.
    """
    try:
        src = Path(path).read_text(encoding="utf-8", errors="replace")
    except OSError:
        return None
    return from_source(src, path)


def stated_slot(mod: Module, func: str, param: str) -> Witness | None:
    """B2: the annotation the source already states for this slot, if any.

    ⚑ ASKS `iface_infer`, WHICH ALREADY OWNS THIS READ. A second annotation walk here would
    be a second authority on "what does the source state" — the same-name-different-body
    hazard this repo has retired repeatedly, and the two would drift.

    ⚑⚑ IT READS THE TREE THIS MODULE ALREADY HOLDS, NOT THE PATH. The first cut passed
    `Path(mod.path)` to `interface_of`, which re-reads from DISK — so a Module built from
    source text (every selftest fixture, and any caller analysing an unsaved edit) silently
    resolved against a file that does not exist, and every slot came back UNRESOLVED. The
    suite caught it only because the discriminator arm demanded a NON-unresolved answer; a
    one-armed case would have stayed green while the reader answered nothing at all.
    """
    iface = iface_infer.interface_of_src(ast.unparse(mod.tree), mod.name)
    for sym in iface.symbols:
        if sym.name != func:
            continue
        where = f"{mod.path}:{sym.lineno}"
        if param == RETURN_SLOT:
            if sym.returns is not None and sym.returns not in iface_infer.HOLLOW:
                return Witness(sym.returns, where, "annotated")
            return None
        for p in sym.params:
            if p.name == param and p.stated and p.annotation is not None:
                return Witness(p.annotation, where, "annotated")
    return None


def binds(mod: Module, func: str, home: str) -> bool:
    """Report whether `mod`'s calls to `func` can reach the def living in `home`.

    ⚑⚑⚑ A SHARED NAME IS NOT A SHARED DEF, AND THIS READER COMMITTED THAT DEFECT. Measured
    live on `check_carrier_locality.scan`: `pycodemod --calls scan` reports **3 defs** and
    35 calls, and the first cut attributed every one of those calls to whichever def was
    being resolved — so `scan#paths` came back witnessed by `_pycodemod_placement.py`,
    a module that calls a DIFFERENT `scan` entirely. That is not a cosmetic mis-attribution:
    a foreign call site can manufacture a CONFLICT, or worse, agree and yield a confident
    wrong type with a `file:line` that looks like proof.

    ⚑⚑ SO A CALL COUNTS ONLY WHERE THE NAME CAN RESOLVE TO THIS DEF — the defining module
    itself, or a module that IMPORTS it from there. The test is deliberately conservative:
    an unresolvable-but-real edge is dropped, which UNDER-reports (a slot reads unresolved
    when evidence existed). Under-reporting is the safe direction here, because the residue
    is printed as a finding while a wrong type is printed as an answer.

    ⚑ AND THAT CONSERVATISM IS EXACTLY WHY `UNCALLED` REFUSES TO SAY "DEAD". This predicate
    can only ever under-count the edges, so a zero it produces is a statement about what
    this walk could RESOLVE, never about what exists.
    """
    if Path(mod.path).absolute() == Path(home).absolute():
        return True
    stem = Path(home).stem
    for node in ast.walk(mod.tree):
        if isinstance(node, ast.ImportFrom) and node.module == stem:
            if any(a.name == func for a in node.names):
                return True
        elif isinstance(node, ast.Import) and any(
            a.name == stem and a.asname is None for a in node.names
        ):
            return True
    return False


def calls_in(mod: Module, func: str) -> list[tuple[str, ast.Call, Module]]:
    """Return every call to `func` inside ONE already-parsed module.

    ⚑ A `__main__` GUARD IS AN ORDINARY CALL AND THIS ALREADY SEES IT. `ast.walk` descends
    into the `if __name__ == "__main__":` body like any other statement, so `main()` there
    is a static call site here exactly as `pycodemod --calls main` indexes it. This is
    recorded because the opposite was assumed: a "dynamic entry" kind was proposed for
    `main#argv` on the belief that the guard was invisible. It is not — the slot reads
    unreached for a different reason entirely, which `unreached_kind` names.
    """
    return [
        (f"{mod.path}:{node.lineno}", node, mod)
        for node in ast.walk(mod.tree)
        if isinstance(node, ast.Call) and iface_bottom.callee_name(node) == func
    ]


class CallIndex:
    """Every call in the corpus, indexed by callee name, from ONE pass.

    ⚑⚑⚑ THE COST LAW WAS O(OWED SLOTS * CORPUS) AND THIS IS WHAT MAKES IT O(CORPUS + SLOTS).
    `_parameter` called `call_sites`, which `load`ed and `ast.walk`ed the ENTIRE corpus once
    PER SLOT. `Resolver.memo` is keyed on the SLOT, so it prevents re-resolving a slot and does
    nothing about re-scanning the corpus for the next one. Measured by `iface_cost --counts`:
    `check_carrier_locality`'s owed slots each bought a full sweep, and `agda_lex` exited 124
    at a 600s timeout without finishing.

    ⚑⚑⚑ A PARSE MEMO IS NOT THIS FIX, AND THE NUMBERS ARE WHY. `iface_cost --cache` measures a
    memo's end-to-end gain against a redundancy RATIO several times larger — because a sweep
    re-parses AND re-walks (`calls_in`, `binds`), and a memo removes only the first half. This
    removes both: the walk happens once and every later query is a dict lookup. **A ratio from
    a counter is an upper bound on a fix, never its value**, which is exactly why the index is
    built rather than the memo.

    ⚑⚑ `binds` IS NOT FOLDED INTO THE INDEX, AND THAT IS THE CORRECTNESS CONSTRAINT. Whether a
    caller can reach a def depends on the DEFINING module (`here.path`), which varies per
    query — so the index stores every call under its callee NAME and the reachability filter
    is applied at LOOKUP, unchanged. Folding it in would key the index on a pair and make it
    answer a narrower question than the one asked, which is how a cost fix becomes a wrong
    answer that merely looks fast.

    ⚑ THE INDEX IS KEYED ON THE CALLEE NAME BECAUSE THAT IS WHAT `calls_in` MATCHED ON. It is
    the same predicate (`iface_bottom.callee_name(node) == func`) evaluated once per node
    instead of once per node per slot; nothing about WHICH calls exist changes.

    ⚑ AN UNPARSEABLE FILE IS SKIPPED HERE EXACTLY AS `call_sites` SKIPPED IT — `load` returns
    None and the file contributes nothing. Same population, same omissions.
    """

    def __init__(self, paths: list[str]) -> None:
        """Record the population; the walk itself is DEFERRED until a slot needs it."""
        self.paths = paths
        self._by_name: dict[str, list[tuple[str, ast.Call, Module]]] | None = None

    @property
    def by_name(self) -> dict[str, list[tuple[str, ast.Call, Module]]]:
        """Walk the corpus ONCE, on first use, bucketing every call by the name it calls.

        ⚑⚑⚑ LAZY, AND `iface_cost`'s SUITE IS WHAT FORCED THAT — THE FIRST CUT BUILT THIS
        EAGERLY AND A CASE WENT RED FOR THE RIGHT REASON. `iface_cost --selftest` pins that a
        FULLY ANNOTATED module sweeps the corpus ZERO times: `_compute` returns STATED before
        `_parameter` is ever reached, so a module with nothing owed should cost nothing. An
        index built in `__init__` charges every walk one sweep whether or not a slot needs it
        — which taxes exactly the annotated modules the surrounding arc exists to produce, and
        makes the instrument report a sweep the walk did not need.

        ⚑⚑ SO THE COST IS PAID BY THE FIRST OWED SLOT AND BY NO ONE ELSE. Zero owed slots is
        zero sweeps (the property the case pins); one or eighty is one sweep. That is the
        O(corpus + slots) law stated honestly at both ends, rather than at the busy end only.

        ⚑ A `None` SENTINEL, NEVER AN EMPTY-DICT TEST. A corpus whose files hold no calls at
        all indexes to `{}`, and a falsy test would re-walk the whole population on every
        query — the re-derivation this class exists to remove, reintroduced in its own guard.
        """
        if self._by_name is not None:
            return self._by_name
        built: dict[str, list[tuple[str, ast.Call, Module]]] = {}
        for p in self.paths:
            mod = load(p)
            if mod is None:
                continue
            for node in ast.walk(mod.tree):
                if not isinstance(node, ast.Call):
                    continue
                name = iface_bottom.callee_name(node)
                if name:
                    built.setdefault(name, []).append((f"{mod.path}:{node.lineno}", node, mod))
        self._by_name = built
        return built

    @property
    def walked(self) -> bool:
        """Report whether the corpus walk has actually happened yet.

        ⚑ THE LAZINESS IS OBSERVABLE, because a property nothing can check is a claim rather
        than a guarantee. `iface_cost` measures the same fact indirectly through the loader
        counter; this lets the suite ask it of the index directly, so a future edit that
        builds eagerly fails here instead of only in the other module's instrument.
        """
        return self._by_name is not None

    def sites(self, func: str, here: Module | None) -> list[tuple[str, ast.Call, Module]]:
        """Return the calls to `func` that can REACH the def living in `here`.

        ⚑⚑ THE DE-DUPLICATION SURVIVES VERBATIM, and it is the half most easily lost. `here`
        arrives spelled the way the CALLER typed it while the corpus yields absolute paths, so
        the defining module's own calls come from `calls_in(here, ...)` and every indexed row
        resolving to that same absolute path is skipped. A path-name comparison missed once
        already and double-counted every in-module site — a duplicated witness inflates
        agreement and can manufacture a CONFLICT from one call.
        """
        out: list[tuple[str, ast.Call, Module]] = list(
            calls_in(here, func) if here is not None else []
        )
        if here is None:
            return out
        mine = Path(here.path).absolute()
        for where, node, mod in self.by_name.get(func, []):
            if Path(mod.path).absolute() == mine:
                continue
            if binds(mod, func, here.path):
                out.append((where, node, mod))
        return out


def call_sites(
    func: str, paths: list[str], here: Module | None = None
) -> list[tuple[str, ast.Call, Module]]:
    """Return every call to `func` across the given corpus paths, with its module.

    ⚑ THE POPULATION IS THE CORPUS, NOT THE FILE. A parameter's type is determined by who
    CALLS it, and restricting the search to the defining module would answer a narrower
    question while looking like the real one — reporting a slot as dead because its only
    caller lives next door. This is the same index `pycodemod --calls` produces.

    ⚑⚑ AND THE DEFINING MODULE IS PASSED IN RATHER THAN RE-READ, for the same reason
    `stated_slot` takes the tree: a Module built from source text has no file behind it, so
    re-loading its path yields None and its own call sites vanish.

    ⚑⚑⚑ THE DE-DUPLICATION IS BY RESOLVED PATH, AND A NAME COMPARISON GOT IT WRONG. `here`
    arrives spelled the way the CALLER typed it (`scripts/x.py`) while `corpus.py_files`
    yields absolute paths, so a `p == here.path` test missed and every call site in the
    defining module was counted TWICE — once under each spelling. That is not cosmetic: a
    duplicated witness inflates agreement, and had the two readings ever DISAGREED it would
    have manufactured a CONFLICT out of one site. Exactly the census-keyed-on-one-spelling
    defect this repo has recorded, in the reader built to carry witnesses.

    ⚑⚑ THIS IS THE ONE-SHOT SPELLING AND `CallIndex` IS THE AMORTISED ONE. Both answer the
    identical question; a `Resolver` builds the index once and asks it per slot, while a
    caller with a single question pays one sweep here rather than indexing a corpus it will
    consult once. Kept because the selftest and any external caller ask exactly one.
    """
    return CallIndex(paths).sites(func, here)


def positional_names(fn: ast.FunctionDef | ast.AsyncFunctionDef) -> list[str]:
    """Return the positionally-bindable parameter names, in declaration order."""
    return [a.arg for a in (*fn.args.posonlyargs, *fn.args.args)]


def bound_argument(
    node: ast.Call, fn: ast.FunctionDef | ast.AsyncFunctionDef, param: str
) -> ast.expr | None:
    """Return the argument expression bound to `param` at one call site.

    ⚑ POSITIONAL AND KEYWORD BOTH, because a call spelling an argument by keyword is the
    same edge as one spelling it positionally. A reader seeing only one under-counts the
    evidence and reports a well-witnessed slot as unresolved — an absence wearing a
    finding's clothes.
    """
    for kw in node.keywords:
        if kw.arg == param:
            return kw.value
    names = positional_names(fn)
    if param in names:
        i = names.index(param)
        if i < len(node.args):
            return node.args[i]
    return None


def returned_types(fn: ast.FunctionDef | ast.AsyncFunctionDef, path: str) -> list[Witness]:
    """Return every `return` expression's given type — the OUTPUT half of the slot set.

    ⚑ THE OUTPUT/INPUT ASYMMETRY IS PRESERVED AND LABELLED, NOT DISSOLVED. A computed
    return is a fact about TODAY'S BODY; a computed parameter is a fact about the CONTRACT
    that any caller must meet. Both are reported, and the witness `kind` carries the
    difference so a reader can weigh them differently rather than having this module weigh
    them on their behalf.
    """
    out: list[Witness] = []
    for node in ast.walk(fn):
        if isinstance(node, ast.Return) and node.value is not None:
            where = f"{path}:{node.lineno}"
            got = iface_bottom.given_type(node.value, where)
            out.append(
                got
                if got is not None
                else Witness("?", where, "return-unresolved", ast.unparse(node.value)[:50])
            )
    return out


class Resolver:
    """The recursive walk, its memo, and its in-progress set.

    ⚑ A CLASS BECAUSE THE CYCLE SET IS STATE THE RECURSION CARRIES, and threading it through
    a free function's parameters is how a second caller ends up with its own copy that
    disagrees. One resolver, one memo, one in-progress set — and the memo is what bounds the
    walk to one visit per slot over a finite graph.
    """

    def __init__(self, paths: list[str]) -> None:
        """Index the corpus population this resolver answers over."""
        self.paths = paths
        self.memo: dict[str, Computed] = {}
        self.active: set[str] = set()
        # ⚑ ONE ORIGINS PER RESOLVER, for the same reason there is one memo: the fixture
        # extents of a witnessing file are a property of the CORPUS, not of the slot being
        # asked about, so a per-slot instance would re-parse `tests/` once per question.
        self.origins = Origins()
        # ⚑⚑⚑ AND ONE CALL INDEX, WHICH IS THE SAME ARGUMENT REACHING THE DOMINANT COST. The
        # memo above already says a per-slot re-derivation of a CORPUS-wide fact belongs on
        # the resolver; `call_sites` was re-deriving exactly that — every call in the tree —
        # once per owed slot, because the memo keys on the slot and so cannot see the sweep
        # underneath it. The set of calls is a property of the corpus, not of the question.
        self.index = CallIndex(paths)

    def resolve(self, mod: Module, func: str, param: str) -> Computed:
        """Compute one slot, recursing through call sites until it bottoms out.

        ⚑ THE CYCLE CHECK IS FIRST AND IT REPORTS, NEVER DEFAULTS. Re-entering a slot means
        its evidence leads back to itself. That is a genuine structural fact about the
        corpus, and the honest answer is to name the loop — not to break it with `Any` and
        present the result as computed.
        """
        key = f"{mod.name}.{func}#{param}"
        if key in self.memo:
            return self.memo[key]
        if key in self.active:
            return Computed(key, (), "CYCLE", "evidence leads back to this slot; no bottom reached")
        self.active.add(key)
        try:
            got = self._compute(key, mod, func, param)
        finally:
            self.active.discard(key)
        self.memo[key] = got
        return got

    def _compute(self, key: str, mod: Module, func: str, param: str) -> Computed:
        """Gather every witness for one slot and classify what they add up to."""
        stated = stated_slot(mod, func, param)
        if stated is not None:
            return Computed(key, (stated,), "STATED", "already annotated at source")
        fn = mod.functions.get(func)
        if fn is None:
            return Computed(key, (), "UNRESOLVED", f"no top-level def named {func}")
        if param == RETURN_SLOT:
            return self._return(key, fn, mod)
        return self._parameter(key, fn, mod, func, param)

    def _return(
        self, key: str, fn: ast.FunctionDef | ast.AsyncFunctionDef, mod: Module
    ) -> Computed:
        """Classify the return slot from its return expressions alone.

        ⚑⚑⚑ A RETURN SLOT IS THE JOIN OF *EVERY* RETURN, AND DROPPING THE UNRESOLVED ONES
        MANUFACTURED A WRONG ANSWER. Measured live on `check_carrier_locality.carrier_of`,
        which returns `parts[0].split()[0]` OR `None`: the first cut filtered the
        unresolved arm away, found the survivors unanimous, and reported a confident
        `NoneType` — precisely inverting the truth, since `None` is the *fallback* arm.

        ⚑⚑ SO A PARTIALLY-RESOLVED RETURN IS UNRESOLVED, NOT A MAJORITY VOTE. This is the
        module's own discipline applied to itself: everywhere else it refuses to pick among
        disagreeing witnesses, and here it was silently picking among the ones it happened
        to understand. What survives is REPORTED — the note names how many arms resolved —
        because "one of the two returns is `None`" is worth reading even when the join is
        not a type.
        """
        ws = tuple(returned_types(fn, mod.path))
        good = tuple(w for w in ws if w.kind != "return-unresolved")
        if not ws:
            return self._no_valued_return(key, fn, mod)
        if len(good) < len(ws):
            return Computed(
                key,
                good,
                "UNRESOLVED",
                f"{len(ws) - len(good)} of {len(ws)} return expression(s) "
                f"did not bottom out — a join over only the resolved arms "
                f"would invert the answer",
            )
        return self._judge(key, good, position="return")

    def _judge(self, key: str, ws: tuple[Witness, ...], *, position: str) -> Computed:
        """Apply the provenance downgrade, then the positional verdict.

        ⚑⚑ PROVENANCE IS ASKED FIRST, AND THE ORDER IS THE WHOLE POINT OF Ⓝ104f. `_verdict`
        answers *do these witnesses agree*; that question is well-posed only once the
        witnesses are known to be about the CONTRACT. A fixture-only slot whose fixtures
        happen to agree would otherwise pass `_verdict` unanimously and ship as COMPUTED —
        which is exactly the invisible half of the defect, the half no CONFLICT ever surfaced.

        ⚑ BOTH POSITIONS ROUTE THROUGH HERE, because a RETURN can be fixture-only too: a
        helper that only a `_selftest` calls has its return arms read from a body no
        production path ever executes. Wiring the downgrade into only the parameter site
        would have fixed the three measured instances and left the class open.
        """
        note = fixture_only(ws, self.origins)
        if note:
            return Computed(key, ws, "FIXTURE", note)
        return Computed(key, ws, _verdict(ws, position=position))

    def _no_valued_return(
        self, key: str, fn: ast.FunctionDef | ast.AsyncFunctionDef, mod: Module
    ) -> Computed:
        """Classify a function with no valued return — usually `None`, occasionally not.

        ⚑⚑⚑ THIS WAS THE STRONGEST BOTTOMING-OUT CASE IN THE SET, FILED AS A FAILURE. The
        retired line — *"no return statement with a value"* — printed
        `gen_build_makefiles.kahn_check#<return>` and `main#<return>` in the residue beside
        genuinely unresolved slots, while `kahn_check`'s authored stub says `-> None` and the
        SOURCE states it as plainly as a literal does: the body ends, so the value is `None`.
        A reader that can say `str` from a `"x"` could always have said `None` from a body
        that falls off its end; it simply had no rule for it.

        ⚑⚑ AND THE ABSENCE OF A VALUED RETURN IS NOT BY ITSELF THE ANSWER, which is why the
        rule lives in `iface_bottom.returns_none` behind three exclusions rather than here
        behind none. A generator, a function whose every exit raises, and a `while True:`
        with no break all have no valued return and are all NOT `None` —
        `gen_build_makefiles.jobs` is the live near-miss, raising `SystemExit` on two arms in
        the same module as the two functions this rule was written for. When the exclusions
        fire, the slot stays a finding and the note says WHICH shape stopped it, because
        "this is a generator" is a fact about the function rather than a limit on the reader.
        """
        got = iface_bottom.returns_none(fn, mod.path)
        if got is not None:
            return Computed(
                key, (got,), "COMPUTED", "no valued return and the body falls through — `None`"
            )
        return Computed(
            key,
            (),
            "UNRESOLVED",
            "no valued return, and the body does not fall through to one "
            "(a generator, a raise-only exit, or a non-breaking loop) — so "
            "`None` would be a claim about a value no caller receives",
        )

    def _parameter(
        self,
        key: str,
        fn: ast.FunctionDef | ast.AsyncFunctionDef,
        mod: Module,
        func: str,
        param: str,
    ) -> Computed:
        """Join the BACKWARD body requirement with every FORWARD call-site argument.

        ⚑ THE SITE COUNT AND THE BOUND COUNT ARE DIFFERENT NUMBERS AND BOTH ARE KEPT.
        `sites` counts calls that REACH this def at all; `reached` counts those that BIND
        this particular slot. The first cut kept only `reached`, and that single number is
        what forced three different facts through one verdict string: with `reached == 0`
        alone there is no way to tell a def nothing calls from a def everything calls while
        omitting one argument. `unreached_kind` needs both.
        """
        ws = iface_bottom.required_of(fn, param, mod.path)
        reached = 0
        sites = 0
        for where, node, caller in self.index.sites(func, mod):
            sites += 1
            arg = bound_argument(node, fn, param)
            if arg is None:
                continue
            reached += 1
            got = iface_bottom.given_type(arg, where)
            ws += [got] if got is not None else self._one_hop(arg, caller, where)
        if not ws:
            if reached:
                return Computed(
                    key, (), "UNRESOLVED", "every incoming argument is itself unresolved"
                )
            return self._unreached(key, fn, mod, param, sites)
        return self._judge(key, tuple(ws), position="parameter")

    def _unreached(
        self,
        key: str,
        fn: ast.FunctionDef | ast.AsyncFunctionDef,
        mod: Module,
        param: str,
        sites: int,
    ) -> Computed:
        """Classify a slot no argument bound, and TYPE its default when it has one.

        ⚑⚑ `unreached_kind` NAMES THE FACT; THIS READS THE EVIDENCE THAT FACT POINTS AT.
        `DEFAULTED` already says the slot is determined at the def rather than owed by a
        caller — and its own docstring records that reading the default's TYPE was left as a
        separate job. This is that job: `default_of` finds the expression (it owns the
        right-alignment), `iface_bottom.default_type` types it, and the witness carries the
        `file:line` of the default itself.

        ⚑⚑⚑ A `None` DEFAULT DOES NOT PROMOTE THE SLOT, AND THAT IS THE WHOLE CARE HERE.
        `= None` witnesses only the `None` ARM of what is nearly always a `T | None`;
        `check_carrier_locality.scan(paths=None)` has an authored stub of
        `Iterable[str] | None`, so reporting a confident `NoneType` would be a WRONG type
        carrying a `file:line` — the `carrier_of` majority-vote inversion in a new position,
        and strictly worse than the honest non-answer it replaced. So a partial witness is
        ATTACHED for the reader to see and the status stays `DEFAULTED`; only a TOTAL default
        (`= 0`, `= "x"`, `= ()`) resolves the slot.
        """
        kind, note = unreached_kind(fn, param, sites)
        default = default_of(fn, param)
        if default is None:
            return Computed(key, (), kind, note)
        got = iface_bottom.default_type(default, mod.path)
        if got is None:
            return Computed(key, (), kind, note)
        if got.partial:
            return Computed(
                key,
                (got,),
                kind,
                f"{note}; the default is `None`, which witnesses only that ARM "
                f"— the other needs the body or a call site",
            )
        return Computed(
            key, (got,), "COMPUTED", "determined by the DEFAULT the def states, not by any caller"
        )

    def _one_hop(self, arg: ast.expr, caller: Module, where: str) -> list[Witness]:
        """Recurse ONE hop: an argument that is itself a parameter of its enclosing def.

        ⚑ THIS IS THE HOP THE OPERATOR NAMED, and it is where the recursion actually
        recurses. `f(p)` inside `def g(p)` means f's slot is determined by g's slot, so ask
        g's — through `resolve`, which is what makes the in-progress set load-bearing rather
        than decorative. The witnesses come back re-labelled with the hop, so a reader can
        see the chain rather than a type that appeared from nowhere.
        """
        if not isinstance(arg, ast.Name):
            return []
        line = int(where.rsplit(":", 1)[1])
        for enclosing in caller.functions.values():
            covers = enclosing.lineno <= line <= (enclosing.end_lineno or line)
            if not covers or arg.id not in positional_names(enclosing):
                continue
            up = self.resolve(caller, enclosing.name, arg.id)
            return [
                Witness(w.type_name, w.where, f"via {enclosing.name}", w.detail)
                for w in up.witnesses
            ]
        return []

    def module_interface(self, mod: Module) -> list[Computed]:
        """Compute every slot of every public function in one module."""
        out: list[Computed] = []
        for name, fn in sorted(mod.functions.items()):
            if name.startswith("_") and not name.startswith("__"):
                continue
            out += [
                self.resolve(mod, name, a.arg)
                for a in (*fn.args.posonlyargs, *fn.args.args, *fn.args.kwonlyargs)
                if a.arg not in iface_infer.IMPLICIT
            ]
            out.append(self.resolve(mod, name, RETURN_SLOT))
        return out


# ⚑⚑⚑ THE FIXTURE-REGION DELIMITER, AND IT IS MEASURED RATHER THAN GUESSED. `pycodemod
# --calls _selftest` reports **103 defs** of that exact name across this corpus — a convention
# near-universal enough that a name test over it reads the tree rather than assuming about it.
# Both live defects land inside one: `agda_lex._selftest` (:1188) encloses the `binds_at`
# fixtures at :1441-1450, and `tsdbprobe._selftest` (:783) encloses the `extract_values` and
# `transitions` fixtures at :819-846.
#
# ⚑⚑ THE HELPERS MUST COUNT TOO, AND THIS MODULE ITSELF IS THE PROOF. `iface_dataflow`'s own
# fixtures live in `_cases_given` and `_census_case`, NOT in `_selftest` — so a delimiter
# reading only that one name would classify the READER's own test data as production evidence,
# which is the defect one level up. Hence a name FAMILY, stated once here rather than at each
# site that has to ask.
_FIXTURE_DEFS = ("_selftest", "_self_test")
_FIXTURE_AFFIX = ("_case", "_cases", "_fixture", "_fixtures")

# ⚑ THE FILE-LEVEL HALF: a path whose whole job is testing. `tests` as a path COMPONENT, never
# a substring — the `build` vs `rebuild` lesson `corpus.excluded` already paid for — plus the
# two filename conventions this corpus uses.
_FIXTURE_DIR = "tests"


@dataclass(frozen=True, slots=True)
class Origin:
    """Where one witness came from: a class, plus the checkable reason for that class.

    ⚑ THE REASON TRAVELS WITH THE VERDICT, because `fixture` on its own is the same
    unwitnessed claim this module refuses everywhere else. `inside a fixture def at
    tsdbprobe.py:783` and `test_agda_lex_paths.py is a test FILE` are both checkable at a
    `file:line` by a reader who does not trust the classifier.
    """

    kind: str
    why: str


def fixture_named(name: str) -> bool:
    """Report whether a def name belongs to the fixture family.

    ⚑ THE AFFIX TEST IS ANCHORED AT BOTH ENDS SO IT CANNOT SWALLOW PRODUCTION NAMES. `_case`
    as a bare substring would also match `lower_case`, `switch_cases` and `edge_case_handler`
    — live names whose evidence a census must not silently downgrade. Requiring a leading `_`
    AND a matching tail keeps the family narrow, which is the safe direction: a fixture this
    misses is reported as production (the status quo), while a production def it wrongly
    caught would suppress real evidence.
    """
    if name in _FIXTURE_DEFS:
        return True
    if not name.startswith("_"):
        return False
    # ⚑⚑ THE AFFIX SITS AT EITHER END, AND THE SUITE CAUGHT THAT A TAIL TEST ALONE MISSES
    # THIS MODULE'S OWN HELPERS. `_census_case` and `_prov_fixture` carry it as a SUFFIX;
    # `_cases_given` carries it as a PREFIX — and `_cases_given` is where `iface_dataflow`
    # keeps its own test data. A delimiter that classified the reader's own fixtures as
    # production is the defect one level up, and it went green until the discriminator asked.
    return any(name.endswith(a) or name.startswith(f"{a}_") for a in _FIXTURE_AFFIX)


def fixture_file(path: str) -> bool:
    """Report whether a whole FILE is test material, from its path alone."""
    p = Path(path)
    return _FIXTURE_DIR in p.parts or p.name.startswith("test_") or p.stem.endswith("_selftest")


class Origins:
    """Classify a witness's `file:line` as production or fixture, memoised per file.

    ⚑ A CLASS BECAUSE THE PARSE IS THE COST. Deciding one witness needs the WITNESSING file's
    def extents; a slot's witnesses cluster into a handful of files while a corpus census asks
    the question tens of thousands of times. One resolver, one memo — the same reason
    `Resolver` is a class.

    ⚑⚑ IT OPENS THE FILE THE WITNESS NAMES, NOT THE MODULE UNDER ANALYSIS, and that is the
    whole point: the defect is evidence arriving from ELSEWHERE, so the classifier must be
    able to look elsewhere. `agda_files#include_build`'s only witness lives in `tests/`, a
    file the walk of `scratch/agda_lex.py` never parses.

    ⚑⚑⚑ A FILE IT CANNOT OPEN IS `production`, DELIBERATELY, AND THE DIRECTION IS THE CARE. An
    unreadable or unparseable file is a fact about THIS MACHINE; downgrading a slot on it
    would let a permissions error or a syntax error masquerade as a finding about the corpus —
    a census reporting its own boundary as its subject, which is the failure this repo has
    recorded most often. Failing toward `production` preserves the pre-change verdict, so an
    I/O failure can only ever leave the answer where it already was.
    """

    def __init__(self) -> None:
        """Start with an empty per-file extent cache."""
        self._spans: dict[str, tuple[tuple[int, int], ...]] = {}

    def _fixture_spans(self, path: str) -> tuple[tuple[int, int], ...]:
        """Return the line extents of every fixture-family def in one file."""
        if path in self._spans:
            return self._spans[path]
        spans: tuple[tuple[int, int], ...] = ()
        try:
            tree = ast.parse(
                Path(path).read_text(encoding="utf-8", errors="replace"), filename=path
            )
        except (OSError, SyntaxError, ValueError):
            self._spans[path] = spans
            return spans
        spans = tuple(
            (n.lineno, n.end_lineno or n.lineno)
            for n in ast.walk(tree)
            if isinstance(n, ast.FunctionDef | ast.AsyncFunctionDef) and fixture_named(n.name)
        )
        self._spans[path] = spans
        return spans

    def of(self, w: Witness) -> Origin:
        """Classify one witness by the `file:line` it already carries."""
        path, _, lineno = w.where.rpartition(":")
        if not path or not lineno.isdigit():
            return Origin("production", "no file:line to classify")
        if fixture_file(path):
            return Origin("fixture", f"{Path(path).name} is a test FILE")
        line = int(lineno)
        for lo, _hi in self._fixture_spans(path):
            if lo <= line <= _hi:
                return Origin("fixture", f"inside a fixture def at {Path(path).name}:{lo}")
        return Origin("production", "an ordinary call site or body reference")


def fixture_only(ws: tuple[Witness, ...], origins: Origins) -> str:
    """Return the FIXTURE note when EVERY witness is test material, else the empty string.

    ⚑⚑⚑ THIS IS Ⓝ104f, AND THE CONFLICT THAT EXPOSED IT WAS THE LUCKY CASE.
    `tsdbprobe.extract_values#body` fired at all only because its four `_selftest` fixtures
    DISAGREE with the one production witness. Where fixtures AGREE with production, or are the
    ONLY witness, the slot reported a confident COMPUTED and nothing fired — so the defect is
    invisible in exactly the place the answer looks strongest. Three shapes, all measured:
      * `agda_lex.agda_files#include_build -> bool` — ONE witness, `tests/…:163`, while the
        def's own `include_build=False` was never consulted.
      * `tsdbprobe.transitions#pairs -> list[tuple[int, float]]` — four `_selftest` fixtures
        at :835-841 and nothing else, CONTRADICTING a stub that deliberately says `object`.
      * `agda_lex.binds_at#tok -> str` — every witness inside `_selftest`.

    ⚑⚑ WHY A NEW STATUS AND NOT A FILTER — THIS IS THE DELIVERABLE, NOT THE OMISSION. Dropping
    fixture witnesses would send these slots back to UNCALLED or UNRESOLVED, and that is a
    WORSE report rather than a safer one: it throws away the observation that the only thing
    in this corpus which has ever exercised the slot is a test. A fixture IS real evidence
    about a real call — it is simply evidence about what one author chose to PASS, never about
    what the contract REQUIRES, and the gap between those two is the whole subject of this
    module. So the witnesses stay, their `file:line`s stay, and the STATUS names which kind of
    evidence they are. `FIXTURE` sits outside `RESOLVED`, so `.computed` yields None and no
    consumer can promote a test fixture into a published stub.

    ⚑ ONE PRODUCTION WITNESS RESTORES THE ORDINARY VERDICT, because the fixtures then
    corroborate — or contradict — a real call rather than standing alone. That is exactly
    `extract_values#body`, which must stay a CONFLICT, and it is why this is a test on the
    WITNESS SET rather than on any individual witness.
    """
    if not ws:
        return ""
    seen = [origins.of(w) for w in ws]
    if any(o.kind == "production" for o in seen):
        return ""
    return (
        f"every witness is TEST MATERIAL ({'; '.join(sorted({o.why for o in seen}))}) "
        f"— a fixture records what one author chose to PASS, never what the contract "
        f"REQUIRES, so this is evidence rather than a computed type"
    )


# ⚑ THE COARSE SPELLINGS — a display whose elements did not all bottom out. They are the
# reader's own partial knowledge, so they ABSTAIN from a verdict rather than voting against
# a refined witness of the same constructor. See `_verdict`.
_COARSE = ("tuple[Any, ...]", "list[Any]", "dict[Any, Any]", "set[Any]")


def _consistent(refined: str, names: set[str]) -> bool:
    """Report whether every name in `names` is the same CONSTRUCTOR as `refined`.

    ⚑ THE CONSTRUCTOR MUST MATCH, NOT MERELY THE COARSENESS. `tuple[Any, ...]` abstains in
    favour of `tuple[bool, str]`, but it must NOT abstain in favour of `list[str]` — those
    are different types and their disagreement is real. Comparing the head up to the first
    `[` is what keeps the abstention narrow enough to preserve every true conflict.
    """
    head = refined.split("[", 1)[0]
    return all(n.split("[", 1)[0] == head for n in names)


def _union(names: set[str]) -> str:
    """Spell a set of return-arm types as one union, `None` last.

    ⚑ `NoneType` IS RESPELLED `None`, because that is what a `.pyi` must say — the authored
    stub for `carrier_of` reads `str | None`, and a computed answer spelling the same type
    `NoneType | str` cannot be diffed against it without a reader translating in their head.
    ⚑⚑ AND `None` GOES LAST rather than sorting alphabetically, for that same reason: every
    stub in this tree writes `str | None`, so an alphabetical `None | str` would be a correct
    type that no reader could compare against the artefact it exists to check.
    """
    rest = sorted(n for n in names if n not in ("NoneType", "None"))
    return " | ".join([*rest, "None"]) if len(rest) < len(names) else " | ".join(rest)


def _verdict(ws: tuple[Witness, ...], *, position: str = "parameter") -> str:
    """Return COMPUTED when the witnesses JOIN, CONFLICT when they genuinely disagree.

    ⚑⚑⚑ Ⓝ104g — A RETURN-POSITION JOIN AND A PARAMETER-POSITION JOIN ARE DIFFERENT
    OPERATIONS, AND SHARING ONE VERDICT MADE A CORRECT ANSWER READ AS A BUG. The rule, stated
    once and precisely: **a function has as many return types as it has `return` arms; a
    parameter has exactly one.** So several types in RETURN position is a UNION BY
    CONSTRUCTION — the arms are alternatives the callee genuinely produces, and joining them
    with `|` IS the answer. Several types in PARAMETER position is a DISAGREEMENT — the call
    sites cannot all be right about one slot, and that accusation is the point of CONFLICT.

    ⚑⚑ MEASURED LIVE: `check_carrier_locality.carrier_of#<return>` reported
    `CONFLICT NoneType | str`, which IS its authored stub's `str | None`, arrived at from
    `return parts[0].split()[0]` on one arm and `return None` on the other. Nothing
    disagreed with anything; the reader had one verdict for two different operations.

    ⚑⚑ AND THE ASYMMETRY IS NOT CONVENTIONAL — IT IS WHICH DIRECTION THE EVIDENCE RUNS. A
    return witness is a fact about the callee's OWN body, so two of them are two things the
    SAME author wrote on purpose, in one place, deliberately. A parameter witness is a fact
    about a DIFFERENT module's call, so two of them are two authors who cannot both be right
    about a single declaration. That is why the parameter CONFLICT must SURVIVE this change,
    and `tsdbprobe.extract_values#body` is the live instance the suite pins it against.

    ⚑⚑⚑ A COARSE SPELLING AND A REFINED ONE ARE NOT A DISAGREEMENT, AND READING THEM AS ONE
    MANUFACTURED A CONFLICT OUT OF UNANIMOUS EVIDENCE. Measured live the moment element
    refinement shipped: `check_scratch_independence.promotion_report#<return>` returns
    `(False, [...])` twice and `(not reasons, reasons or [...])` once. The first two refine
    to `tuple[bool, list[str]]` — which is exactly what the authored stub states — while the
    third keeps `tuple[Any, ...]` because `not reasons` does not bottom out. Three witnesses
    that AGREE were reported as `tuple[Any, ...] | tuple[bool, list[str]]`, a CONFLICT the
    corpus does not contain.

    ⚑⚑ THAT IS THIS MODULE'S OWN DEFECT CLASS, POINTED AT ITSELF. A CONFLICT is supposed to
    mean a latent bug — a call site passing the wrong thing — and it is the most expensive
    verdict here precisely because it accuses the code. Inventing one out of the READER's own
    partial knowledge is worse than the coarse answer it replaced: it converts "I refined two
    of three arms" into "your returns disagree". The refinement is a property of what the
    reader could SEE, never of what the source does.

    ⚑ SO A COARSE WITNESS ABSTAINS RATHER THAN VOTING. When exactly one refined type is
    present and every coarse witness shares its constructor, that refined type IS the answer.
    Only genuinely distinct types — `str` beside `int`, or `list[str]` beside `tuple[...]` —
    remain a CONFLICT in parameter position, and two DIFFERENT refined types still conflict.

    ⚑⚑⚑ AND THE ABSTENTION RULE RUNS FIRST, IN BOTH POSITIONS — THAT ORDERING IS LOAD-BEARING
    RATHER THAN INCIDENTAL, AND IT IS THE ONE WAY THIS CHANGE COULD HAVE UNDONE THE PREVIOUS
    REPAIR. `tuple[Any, ...]` beside `tuple[bool, list[str]]` is one refined reading and one
    un-refined one — the READER's own partial knowledge — in a return exactly as much as in a
    parameter. Were the union rule allowed to pre-empt it, `promotion_report#<return>` would
    come back spelled `tuple[Any, ...] | tuple[bool, list[str]]`: a union of a type with its
    own blurrier self, which is not a union of anything, and which would launder the false
    CONFLICT into a false COMPUTED rather than fixing it. Abstain, THEN union.
    """
    names = {w.type_name for w in ws}
    if len(names) == 1:
        return "COMPUTED"
    refined = names - set(_COARSE)
    if len(refined) == 1 and _consistent(next(iter(refined)), names):
        return "COMPUTED"
    return "COMPUTED" if position == "return" else "CONFLICT"


def default_of(fn: ast.FunctionDef | ast.AsyncFunctionDef, param: str) -> ast.expr | None:
    """Return the default expression the DEF gives `param`, or None when it has none.

    ⚑ THE DEFAULTS LIST IS RIGHT-ALIGNED AGAINST THE POSITIONALS, and getting that
    alignment wrong is how a defaulted slot reads as undefaulted or the reverse. Python
    stores `k` defaults for the LAST `k` of `posonlyargs + args`; keyword-only defaults are
    a PARALLEL list with `None` holes, which is a different shape and must be read as one.
    Both are read here, because a keyword-only parameter with a default is exactly as
    determined as a positional one — and a reader that saw only the positional half would
    report every defaulted keyword-only slot as dead.

    ⚑⚑ IT RETURNS THE EXPRESSION, NOT A BOOL, so the caller has a `file:line` to name. That
    is the whole discipline of this module: the answer to "why is this slot not owed by a
    caller" is a location a reader can check, not a claim.
    """
    pos = positional_names(fn)
    n = len(fn.args.defaults)
    tail = pos[len(pos) - n :] if n else []
    if param in tail:
        return fn.args.defaults[tail.index(param)]
    for a, d in zip(fn.args.kwonlyargs, fn.args.kw_defaults, strict=True):
        if a.arg == param and d is not None:
            return d
    return None


def unreached_kind(
    fn: ast.FunctionDef | ast.AsyncFunctionDef, param: str, sites: int
) -> tuple[str, str]:
    """Name WHICH FACT a slot no argument reached reports, as a (status, note) pair.

    ⚑⚑⚑ ONE VERDICT STRING WAS CARRYING THREE DIFFERENT FACTS, AND TWO OF THEM ARE NOT
    DEADNESS AT ALL. The retired wording — *"no call site passes this parameter — the slot
    is DEAD or reached only dynamically"* — handed the reader a disjunction and no way to
    settle it. That is `report-presence-never-absence` committed inside the reader built to
    carry witnesses: a fact about THIS WALK's reach, printed as a fact about the SUBSTRATE.
    `check_stub_authority` went three-valued the same day for the same reason (`not
    verified` is not `verified broken`, because an absent dependency is a fact about the
    MACHINE), and this is that split applied to unreached slots.

    ⚑⚑ THE THREE KINDS ARE SEPARATED BY EVIDENCE THIS WALK ALREADY HOLDS, and each carries
    a DIFFERENT instruction to the reader:

      * DEFAULTED — the def gives the parameter a default, so the slot IS determined and
        the determining expression sits at a `file:line` in the def itself. Nothing is dead
        and no CALLER owes anything. This is the worst of the three to misreport, because
        "dead" invites the DELETION of a live parameter. Reading the default's own type is
        a separate job (⟡bottom-widen) and is deliberately not done here.
      * UNCALLED — nothing in the corpus calls a `func` that `binds` can resolve to this
        def. That is a fact about the CORPUS BOUNDARY, not about the slot: a library entry
        point whose callers are pandoc filters outside this tree reads identical to a
        genuinely dead one, and `binds` is deliberately conservative, so its zero can only
        under-count. This reader therefore names the boundary and refuses to assert death.
      * OMITTED — calls DO reach this def, not one of them binds this slot, and there is no
        default to fall back on. That is not an absence at all; it is a live latent
        `TypeError` waiting on the next execution of one of those sites, and it is the only
        one of the three that is a defect in the code rather than a limit on the reader.

    ⚑⚑⚑ A DYNAMIC ENTRY IS *NOT* A FOURTH KIND, AND THE MEASUREMENT OVERTURNED THE PREMISE.
    This split was commissioned on the reading that `main#argv` under `if __name__ ==
    "__main__"` is a call the index cannot see. It is seen: a guard's `main(...)` is an
    ordinary `ast.Call` in the module's own tree, `calls_in` walks that tree, and
    `pycodemod --calls main` indexes the same site. What the two witnesses offered as
    "genuinely dead" and as "dynamic entry" actually SHARE is a default —
    `check_carrier_locality.scan(paths=None)` and `tsdbprobe.main(argv=None)` — and they
    land, correctly, in one DEFAULTED kind. A kind with no instance is a hypothesis rather
    than a category, so no dynamic kind is shipped. What WOULD be one — a call reaching the
    def through a name this walk cannot resolve (a dispatch table, a `getattr`) — is not
    separable from UNCALLED with what the corpus offers, and is named inside UNCALLED's own
    note rather than given a status it cannot witness.
    """
    default = default_of(fn, param)
    if default is not None:
        return (
            "DEFAULTED",
            (
                f"the def gives this parameter a DEFAULT at line {default.lineno} "
                f"(`{ast.unparse(default)[:_SHOWN_DEFAULT]}`) — determined AT THE DEF, not owed "
                f"by any caller; NOT dead, and reading its type is a separate job"
            ),
        )
    if sites == 0:
        return (
            "UNCALLED",
            (
                "no call in THIS corpus resolves to this def — a fact about the corpus "
                "boundary (a library's callers, or a dynamic dispatch this walk cannot "
                "resolve, may lie outside it), never proof that none exists"
            ),
        )
    return (
        "OMITTED",
        (
            f"{sites} call site(s) reach this def and NONE bind this parameter, which has no "
            f"default — a latent TypeError, not an absence of evidence"
        ),
    )


def _render_stuck(stuck: list[Computed]) -> None:
    """Print the residue GROUPED BY KIND, each group with its own instruction.

    ⚑ GROUPING FOR LAYOUT IS THE OPPOSITE OF COLLAPSING. The old renderer printed one
    paragraph over every unresolved slot saying each was *"either DEAD or reached through
    another unresolved slot"* — so even after the statuses were split, a reader skimming the
    report would still have taken the collapsed reading from the prose above them. The
    header is per-kind for the same reason the status is.
    """
    sys.stdout.write(
        "\n  DID NOT BOTTOM OUT — reported, never filled with `Any`. These are DIFFERENT\n"
        "  facts and the status says which: a DEFAULTED slot is determined at the def and\n"
        "  is NOT dead; an UNCALLED one reports the corpus BOUNDARY, not death; an OMITTED\n"
        "  one is a latent TypeError; UNRESOLVED/CYCLE mean the work is upstream.\n"
    )
    for kind in (*UNREACHED, "UNRESOLVED", "CYCLE"):
        for r in [row for row in stuck if row.status == kind]:
            sys.stdout.write(f"    {r.status:10s} {r.slot}: {r.note}\n")


def _render(rows: list[Computed]) -> int:
    """Print each computed slot with its witnesses, then the unresolved residue."""
    done = [r for r in rows if r.status in RESOLVED]
    conflict = [r for r in rows if r.status == "CONFLICT"]
    fixture = [r for r in rows if r.status == FIXTURE]
    stuck = [r for r in rows if r.status in STUCK]
    tally = ", ".join(
        f"{sum(1 for r in stuck if r.status == k)} {k.lower()}"
        for k in (*UNREACHED, "UNRESOLVED", "CYCLE")
        if any(r.status == k for r in stuck)
    )
    sys.stdout.write(
        f"iface-dataflow: {len(done)} of {len(rows)} slot(s) COMPUTED from the corpus; "
        f"{len(conflict)} conflicting, {len(fixture)} witnessed ONLY by fixtures, "
        f"{len(stuck)} did NOT bottom out"
        f"{' (' + tally + ')' if tally else ''}.\n"
    )
    for r in done + conflict + fixture:
        got = r.computed or " | ".join(r.types)
        sys.stdout.write(f"    {r.status:9s} {r.slot} -> {got}\n")
        for w in r.witnesses[:_SHOWN_WITNESSES]:
            sys.stdout.write(f"          [{w.kind}] {w.where}  {w.detail}\n")
        # ⚑ THE FIXTURE ROW CARRIES ITS NOTE INLINE, beside the type it is NOT claiming.
        # A reader skimming the resolved block would otherwise take the printed type as an
        # answer — the status alone is one column wide and the type is the thing they came
        # for. The note is what says the type is a test's choice, not a contract.
        if r.status == FIXTURE:
            sys.stdout.write(f"          ⚑ {r.note}\n")
    if stuck:
        _render_stuck(stuck)
    return 0


def _render_sites(path: str) -> int:
    """Print mypy's forward Any-propagation trace — the half mypy DOES answer."""
    proc = subprocess.run(  # noqa: S603  - fixed argv, no shell, no user interpolation
        [sys.executable, "-m", "mypy", "--disallow-any-expr", "--no-incremental", path],
        cwd=corpus.ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    lines = [ln for ln in proc.stdout.splitlines() if ": error:" in ln]
    sys.stdout.write(
        f"iface-sites: mypy names {len(lines)} expression(s) whose type collapsed to "
        f"`Any` in {path}.\n"
        "  ⚑ A FORWARD TRACE, NOT AN ANSWER. Each line says `Any` ARRIVED here and from\n"
        "  which unannotated def. None says what the type OUGHT to be: a checker types a\n"
        "  call by reading the parameter's declaration, and with none it writes `Any` and\n"
        "  never asks what the argument was. `--module` asks that.\n"
    )
    for ln in lines[:_SHOWN_SITES]:
        sys.stdout.write(f"    {ln}\n")
    return 0


def _dispatch_slot(rest: list[str]) -> int:
    """Run `--slot`, which needs a path, a function and optionally a parameter."""
    if len(rest) < _SLOT_MIN_OPERANDS:
        sys.stdout.write("--slot needs <path> <func> [param]\n")
        return 2
    mod = load(rest[0])
    if mod is None:
        sys.stdout.write(f"could not parse {rest[0]}\n")
        return 2
    param = rest[2] if len(rest) > _SLOT_MIN_OPERANDS else RETURN_SLOT
    return _render([Resolver(corpus.py_files()).resolve(mod, rest[1], param)])


def _dispatch_module(rest: list[str]) -> int:
    """Run `--module`, computing every public slot of one module."""
    if not rest:
        sys.stdout.write("--module needs <path>\n")
        return 2
    mod = load(rest[0])
    if mod is None:
        sys.stdout.write(f"could not parse {rest[0]}\n")
        return 2
    return _render(Resolver(corpus.py_files()).module_interface(mod))


def census(paths: list[str]) -> dict[str, list[str]]:
    """Return every not-bottomed-out slot in the corpus, keyed by status.

    ⚑⚑⚑ THIS MODE EXISTS BECAUSE A SPREAD CANNOT ANSWER AN EXISTENCE QUESTION, AND ONE WAS
    ABOUT TO BE ANSWERED WITH ONE. A 30-module sample found `UNCALLED` abundantly and
    `OMITTED` not at all, and the standing rule — a kind with no live instance is a
    hypothesis, not a category — would have deleted `OMITTED` on that reading. But "none in
    the 30 I looked at" is a fact about the SAMPLE, and deleting a classifier arm on it is
    precisely `report-presence-never-absence`: the same error this module was split to fix,
    one level up, in the decision about the fix.

    ⚑⚑ AND THE HONEST INSTRUMENT WAS A MISSING MODE, NOT A MISSING FACT. The repo's standing
    rule says a toolkit gap is WORK; the population is `corpus.py_files`, the classifier
    already runs per slot, and nothing but a loop was absent. So the existence question is
    put to the whole corpus and answered with a denominator rather than settled by sampling.
    """
    # ⚑⚑ `FIXTURE` IS CENSUSED HERE FOR THE REASON THIS MODE EXISTS AT ALL. The three
    # measured instances were found by hand, one module at a time, which is a SAMPLE — and
    # this docstring already records that answering an existence question from a sample is
    # how `OMITTED` nearly got deleted. A new status that cannot be counted over the
    # population is a hypothesis with three anecdotes attached, so it joins the denominator.
    out: dict[str, list[str]] = {k: [] for k in (*UNREACHED, FIXTURE)}
    res = Resolver(paths)
    for p in paths:
        mod = load(p)
        if mod is None:
            continue
        try:
            rows = res.module_interface(mod)
        except RecursionError:
            continue
        for r in rows:
            if r.status in out:
                out[r.status].append(r.slot)
    return out


def _render_census(paths: list[str]) -> int:
    """Print how many slots of each unreached kind the whole corpus holds."""
    found = census(paths)
    sys.stdout.write(
        f"iface-census: {len(paths)} module(s) walked. Each count below is a POPULATION, "
        f"so a zero is a zero over this whole corpus — not over a sample.\n"
    )
    for kind in (*UNREACHED, FIXTURE):
        slots = found[kind]
        sys.stdout.write(f"    {kind:10s} {len(slots)}\n")
        for s in slots[:_SHOWN_WITNESSES]:
            sys.stdout.write(f"          {s}\n")
    return 0


def main(argv: list[str]) -> int:
    """Dispatch one mode; 2 on an unusable command line."""
    rest = [a for a in argv[1:] if not a.startswith("-")]
    if "--sites" in argv:
        if not rest:
            sys.stdout.write("--sites needs <path>\n")
            return 2
        return _render_sites(rest[0])
    if "--census" in argv:
        return _render_census(corpus.py_files(*rest))
    if "--module" in argv:
        return _dispatch_module(rest)
    if "--slot" in argv:
        return _dispatch_slot(rest)
    sys.stdout.write(__doc__ or "")
    return 2


def _shape(c: Computed) -> tuple[str, str | None]:
    """Return a slot's (status, computed type) — the pair most cases compare."""
    return (c.status, c.computed)


def _fn_of(src: str, func: str) -> ast.FunctionDef | ast.AsyncFunctionDef:
    """Return one def from source text — the fixture the kind cases classify."""
    mod = from_source(src, "k.py")
    if mod is None:
        raise TypeError(src)
    return mod.functions[func]


def _slot(src: str, name: str, func: str, param: str) -> Computed:
    """Resolve one slot from source TEXT — the fixture builder the case sets share.

    ⚑ LIFTED TO MODULE SCOPE so `_cases_given` can use it without being handed a closure.
    It was a nested def while `_selftest` was the only caller; a second case set is what
    makes it shared machinery rather than a local.
    """
    mod = from_source(src, name)
    if mod is None:
        raise TypeError(src)
    return Resolver([name]).resolve(mod, func, param)


def _census_case() -> tuple[str, object, object]:
    """Build the case pinning that the census separates all four kinds over a population.

    ⚑⚑ A PER-SLOT CLASSIFIER AND A POPULATION WALK ARE DIFFERENT THINGS TO GET WRONG. The
    `unreached_kind` cases pin the classification of ONE slot; this pins that the census
    carries each verdict into its own bucket. A loop that appended every unreached slot to
    a single list, or that let one module's rows overwrite another's, would pass every one
    of those cases and fail only here.

    ⚑⚑⚑ AND `OMITTED` IS THE ARM THAT MAKES THIS FIXTURE LOAD-BEARING RATHER THAN TIDY. A
    corpus-wide census finds DEFAULTED and UNCALLED in abundance and OMITTED nowhere, and
    the standing rule — a kind with no live instance is a hypothesis, not a category —
    would delete it on that reading. It is kept because the two absences are NOT the same
    kind of absence. The dynamic-entry kind was dropped because NO evidence in the corpus
    could ever SEPARATE it from UNCALLED — an unwitnessable distinction. OMITTED is
    decidable from evidence this walk already holds, and is merely not instantiated in
    committed code, which is what a tree whose selftests pass SHOULD look like: an OMITTED
    slot is a latent `TypeError`. Deleting the arm that detects a defect because the tree
    currently has none would leave the reader unable to report it when it arrives. So the
    kind is witnessed HERE, constructively, and `--census` reports its live zero with a
    denominator rather than a sample.

    ⚑ THE FIXTURE IS WRITTEN TO DISK because `call_sites` resolves its population through
    `load`, which reads files. Threading an in-memory reader through the whole walk would
    add a second code path existing only for the test — and a path the shipped mode does
    not take is one that can drift from it silently.
    """
    tmp = Path(__file__).absolute().parent / "_census_fixture"
    src = {
        # UNCALLED: nothing anywhere calls `u`, so no site reaches the def at all.
        "cu.py": "def u(a):\n    return 1\n",
        # DEFAULTED: `d`'s slot is determined at the def — and the default is `object()`,
        # which `iface_bottom.default_type` cannot type, so the slot STAYS defaulted rather
        # than being resolved out from under this case by a later widening of that reader.
        # OMITTED: `o` IS called, and that call binds nothing to `b`, which has no default.
        "cd.py": "def d(a=object()):\n    return 1\ndef o(b):\n    return 1\no()\n",
        # ⚑⚑ FIXTURE: `x` is called ONLY from a fixture-family def, in an otherwise ordinary
        # production file — the `agda_lex` shape, where the test data is at module scope
        # beside the code rather than in a `tests/` tree. Included so the census SEPARATES
        # four kinds rather than three plus an empty column: a bucket that is only ever empty
        # in the fixture proves nothing about the loop that fills it.
        "cf.py": ('def x(a):\n    return 1\ndef _selftest():\n    x("s")\n'),
    }
    tmp.mkdir(exist_ok=True)
    try:
        paths = []
        for name, text in src.items():
            (tmp / name).write_text(text, encoding="utf-8")
            paths.append(str(tmp / name))
        got = {k: sorted(v) for k, v in census(paths).items()}
    finally:
        for name in src:
            (tmp / name).unlink(missing_ok=True)
        tmp.rmdir()
    return (
        "the census separates all four kinds over a population",
        got,
        {
            "DEFAULTED": ["cd.d#a"],
            "OMITTED": ["cd.o#b"],
            "UNCALLED": ["cu.u#a"],
            "FIXTURE": ["cf.x#a"],
        },
    )


def _cases_given() -> list[tuple[str, object, object]]:
    """Pin the two evidence sources the DEF ITSELF supplies — a default, and a `None` return.

    ⚑ SPLIT OUT BECAUSE THE PER-FILE GATE SAID SO, and the gate read the shape correctly:
    `_selftest` had grown past the statement bound while these cases pin a claim distinct
    from the reach/join/cycle ones. The two sources grouped here share one property — both
    read the DEFINING module's own text rather than any call site — which is also why
    neither can widen the population from which a `tests/` fixture becomes a witness.

    ⚑ IT RETURNS ITS CASES RATHER THAN TAKING A `check` CLOSURE, so no callable type has to
    be spelled and the list stays the one shape `_selftest` already accumulates.
    """
    # ⚑⚑⚑ THE DEFAULT IS NOW TYPED, AND THE TWO ARMS MUST LAND DIFFERENTLY. A TOTAL default
    # determines the slot; a `None` default witnesses only its own arm and must NOT promote
    # it. Asked as one mapping so a reader that resolved BOTH — the `carrier_of` inversion
    # repeated — fails here rather than shipping `NoneType` for a `T | None` parameter.
    dn = _slot("def f(a=None):\n    return 1\n", "dn2", "f", "a")
    return [
        (
            "a total default resolves the slot; a None default only witnesses its arm",
            {
                "total": _shape(_slot('def f(a="x"):\n    return 1\n', "dt", "f", "a")),
                "none": _shape(_slot("def f(a=None):\n    return 1\n", "dn", "f", "a")),
            },
            {"total": ("COMPUTED", "str"), "none": ("DEFAULTED", None)},
        ),
        # ⚑ AND THE PARTIAL WITNESS IS STILL ATTACHED AND STILL LABELLED, because "the
        # default is None" is worth reading even where it is not the answer — suppressing it
        # would trade one silent absence for another.
        (
            "the None default is reported as a partial witness, not dropped",
            [(w.type_name, w.kind, w.partial) for w in dn.witnesses],
            [("NoneType", "default", True)],
        ),
        # ⚑ THE BODY STILL OUTRANKS THE DEFAULT: a slot with a `None` default AND a body
        # requirement resolves on the body, since `_parameter` reaches the default arm only
        # when no other witness exists. Without this the widening could mask a real B4 answer.
        (
            "a body requirement still wins over a None default",
            _shape(_slot('def f(a=None):\n    return a.endswith("x")\n', "db", "f", "a")),
            ("COMPUTED", "str"),
        ),
        # ⚑⚑⚑ A FUNCTION WITH NO VALUED RETURN IS `None`, AND IT WAS FILED AS A FAILURE.
        # Asked as one mapping so all four arms are pinned at once: the rule must fire on a
        # body that falls through and must NOT fire on the three shapes that have no valued
        # return for a different reason. A reader answering `None` to all of them would type
        # `gen_build_makefiles.jobs` — which raises `SystemExit` — as `None` while its
        # authored stub says `int`.
        (
            "a fall-through body is None; a generator, a raise-only and a loop are not",
            {
                "falls-through": _shape(_slot("def f(a):\n    g(a)\n", "n1", "f", RETURN_SLOT)),
                "generator": _shape(_slot("def f(a):\n    yield a\n", "n2", "f", RETURN_SLOT)),
                "raise-only": _shape(
                    _slot('def f(a):\n    raise SystemExit("x")\n', "n3", "f", RETURN_SLOT)
                ),
                "loop-forever": _shape(
                    _slot("def f(a):\n    while True:\n        g(a)\n", "n4", "f", RETURN_SLOT)
                ),
            },
            {
                "falls-through": ("COMPUTED", "None"),
                "generator": ("UNRESOLVED", None),
                "raise-only": ("UNRESOLVED", None),
                "loop-forever": ("UNRESOLVED", None),
            },
        ),
        # ⚑⚑ AND THE ELEMENT-REFINED RETURN, the arm that made a computed tuple coarser than
        # the authored stub. Both directions are asked: a tuple whose elements ALL bottom out
        # is spelled positionally, and one with an unresolved element must STAY coarse rather
        # than refine on the arms it happened to understand.
        (
            "a return tuple refines only when every element bottoms out",
            {
                "all-known": _slot(
                    'def f(a):\n    return (True, "s")\n', "e1", "f", RETURN_SLOT
                ).computed,
                "one-unknown": _slot(
                    "def f(a):\n    return (True, a)\n", "e2", "f", RETURN_SLOT
                ).computed,
            },
            {"all-known": "tuple[bool, str]", "one-unknown": "tuple[Any, ...]"},
        ),
        # ⚑⚑⚑ A COARSE WITNESS ABSTAINS; A GENUINELY DIFFERENT TYPE STILL CONFLICTS. This
        # is the discriminator for the abstention rule, and it exists because the rule was
        # written to REPAIR a false CONFLICT — so the risk it introduces is the opposite
        # error, silently swallowing a true one. Measured live: `promotion_report#<return>`
        # returns a refined `(False, [...])` twice and a coarse `(not reasons, ...)` once,
        # and the first cut called three AGREEING witnesses a CONFLICT.
        #
        # ⚑ ALL THREE ARMS ASKED AT ONCE: a rule that abstained unconditionally would pass
        # the first and fail the other two, and one that never abstained fails only the
        # first. Neither can be green here by accident.
        # ⚑⚑⚑ AND Ⓝ104g REWROTE TWO OF THESE THREE EXPECTATIONS, WHICH IS THE POINT. In
        # RETURN position `str` beside `int` was never a disagreement — a function with two
        # arms has two return types — so `two-scalars` is now the UNION `int | str`, and
        # `two-constructors` is `list[str] | tuple[Any, ...]`. Only the abstention arm keeps
        # its old answer, and it MUST: it is the one case where the two spellings are the
        # reader's own partial knowledge of ONE type rather than two alternatives.
        #
        # ⚑⚑ THE THIRD ARM IS THE REGRESSION GUARD FOR A BUG THIS CHANGE EXPOSED.
        # `two-constructors` first came back a confident `list[str]`, silently DROPPING the
        # tuple arm: `Computed.computed` abstained without the `_consistent` constructor
        # check that `_verdict` has always had, and while every multi-type slot was a CONFLICT
        # that second, weaker copy of the rule was unreachable. Asked here so a future edit
        # that re-drops it fails rather than shipping a narrowed return type.
        (
            "a coarse witness abstains; distinct return arms UNION rather than conflict",
            {
                "coarse-and-refined": _shape(
                    _slot(
                        'def f(a):\n    if a:\n        return (True, "s")\n    return (a, "s")\n',
                        "v1",
                        "f",
                        RETURN_SLOT,
                    )
                ),
                "two-constructors": _shape(
                    _slot(
                        'def f(a):\n    if a:\n        return ["s"]\n    return (a, a)\n',
                        "v2",
                        "f",
                        RETURN_SLOT,
                    )
                ),
                "two-scalars": _shape(
                    _slot(
                        'def f(a):\n    if a:\n        return "s"\n    return 1\n',
                        "v3",
                        "f",
                        RETURN_SLOT,
                    )
                ),
            },
            {
                "coarse-and-refined": ("COMPUTED", "tuple[bool, str]"),
                "two-constructors": ("COMPUTED", "list[str] | tuple[Any, ...]"),
                "two-scalars": ("COMPUTED", "int | str"),
            },
        ),
        # ⚑⚑⚑ THE DISCRIMINATOR ACROSS THE POSITION SEAM, AND IT IS THE ONE CASE THAT CAN
        # CATCH Ⓝ104g APPLIED TOO WIDELY. The SAME two types — `str` and `int` — union in
        # RETURN position and CONFLICT in PARAMETER position, because a function has as many
        # return types as it has arms while a parameter has exactly one. A rule that unioned
        # unconditionally passes the case above and fails here; one that never unioned fails
        # above and passes here. Neither can be green by accident.
        (
            "the SAME two types union in a return and conflict in a parameter",
            {
                "return": _shape(
                    _slot(
                        'def f(a):\n    if a:\n        return "s"\n    return 1\n',
                        "p1",
                        "f",
                        RETURN_SLOT,
                    )
                ),
                "parameter": _shape(
                    _slot('def f(a):\n    return 1\nf("x")\nf(3)\n', "p2", "f", "a")
                ),
            },
            {"return": ("COMPUTED", "int | str"), "parameter": ("CONFLICT", None)},
        ),
        # ⚑⚑ THE `None` ARM IS SPELLED THE WAY A STUB SPELLS IT, and this is the live
        # instance: `check_carrier_locality.carrier_of` returns `parts[0].split()[0]` or
        # `None` and read `CONFLICT NoneType | str`, which IS its authored stub's `str | None`
        # — a union by construction reported as a disagreement. Both halves are pinned: the
        # verdict must be COMPUTED, and the spelling must be diffable against the `.pyi`.
        (
            "a two-arm return with a None arm is the stub's own `str | None`",
            _shape(
                _slot(
                    "def f(a):\n    if a:\n        return 's'\n    return None\n",
                    "u1",
                    "f",
                    RETURN_SLOT,
                )
            ),
            ("COMPUTED", "str | None"),
        ),
        _census_case(),
        *_cases_provenance(),
    ]


def _provenance_fixture() -> tuple[str, object, object]:
    """Build the case pinning that fixture-ONLY evidence does not read COMPUTED.

    ⚑⚑⚑ THE DISCRIMINATOR IS THE WHOLE CASE, because a rule that downgraded EVERYTHING would
    pass a one-armed version of this and destroy the reader. Three call sites bind the same
    slot with the same literal, and they differ ONLY in provenance:
      * `pf_prod.py` — an ordinary module-scope call. PRODUCTION.
      * `test_pf.py` — a `test_`-named FILE. FIXTURE by path.
      * `pf_prod.py:_selftest` — a call inside a fixture-family DEF in an otherwise ordinary
        production file. FIXTURE by region, and this is the subtle half: `agda_lex`'s
        fixtures are at module scope in the same file as production code, so a path-only
        classifier misses them entirely.
    Asked as one mapping so all three land at once. A classifier reading only paths reports
    the region arm COMPUTED; one reading only regions reports the file arm COMPUTED; one
    downgrading unconditionally reports the production arm FIXTURE.

    ⚑⚑ AND THE FOURTH ARM IS THE ONE THAT KEEPS Ⓝ104f FROM SWALLOWING Ⓝ104g. `mixed` has a
    fixture witness AND a production witness that DISAGREE — the shape of the live
    `tsdbprobe.extract_values#body` — and it must stay a CONFLICT. Were provenance to filter
    witnesses rather than classify the SET, the fixture arms would vanish and the conflict
    with them, converting a real finding into a confident wrong answer.

    ⚑ WRITTEN TO DISK for the same reason `_census_case` is: `call_sites` resolves its
    population through `load`, and `Origins` opens the WITNESSING file by path. An in-memory
    path would be a second code path existing only for the test.
    """
    tmp = Path(__file__).absolute().parent / "_prov_fixture"
    src = {
        "pf_prod.py": (
            "def only_prod(a):\n    return 1\n"
            "def only_region(b):\n    return 1\n"
            "def mixed(c):\n    return 1\n"
            'only_prod("x")\n'
            'mixed("x")\n'
            "def _selftest():\n"
            '    only_region("x")\n'
            "    mixed(3)\n"
        ),
        "test_pf.py": (
            'from pf_prod import only_file\ndef only_file(d):\n    return 1\nonly_file("x")\n'
        ),
    }
    tmp.mkdir(exist_ok=True)
    try:
        paths = []
        for name, text in src.items():
            (tmp / name).write_text(text, encoding="utf-8")
            paths.append(str(tmp / name))
        res = Resolver(paths)
        prod = load(str(tmp / "pf_prod.py"))
        tst = load(str(tmp / "test_pf.py"))
        if prod is None or tst is None:
            raise TypeError(str(tmp))
        got = {
            "production": _shape(res.resolve(prod, "only_prod", "a")),
            "fixture-region": _shape(res.resolve(prod, "only_region", "b")),
            "fixture-file": _shape(res.resolve(tst, "only_file", "d")),
            "mixed": _shape(res.resolve(prod, "mixed", "c")),
        }
    finally:
        for name in src:
            (tmp / name).unlink(missing_ok=True)
        tmp.rmdir()
    return (
        "fixture-only evidence is FIXTURE; one production witness restores the verdict",
        got,
        {
            "production": ("COMPUTED", "str"),
            "fixture-region": ("FIXTURE", None),
            "fixture-file": ("FIXTURE", None),
            "mixed": ("CONFLICT", None),
        },
    )


def _cases_provenance() -> list[tuple[str, object, object]]:
    """Pin Ⓝ104f: a witness carries WHERE IT CAME FROM, and the verdict respects it."""
    return [
        # ⚑ THE NAME FAMILY, ASKED WITH ITS NEAR-MISSES. `_selftest` and `_census_case` are
        # fixtures; `lower_case`, `switch_cases` and `edge_case_handler` are production names
        # that a bare `_case` SUBSTRING test would have swallowed — and swallowing a
        # production name is the dangerous direction, because it SUPPRESSES real evidence
        # rather than merely failing to downgrade. `_compute` pins that a leading underscore
        # alone is not enough.
        (
            "the fixture name family is anchored and does not swallow production names",
            {
                n: fixture_named(n)
                for n in (
                    "_selftest",
                    "_census_case",
                    "_cases_given",
                    "_prov_fixture",
                    "lower_case",
                    "switch_cases",
                    "edge_case_handler",
                    "_compute",
                    "main",
                )
            },
            {
                "_selftest": True,
                "_census_case": True,
                "_cases_given": True,
                "_prov_fixture": True,
                "lower_case": False,
                "switch_cases": False,
                "edge_case_handler": False,
                "_compute": False,
                "main": False,
            },
        ),
        # ⚑ THE PATH TEST IS A COMPONENT MATCH, and `contests/` is the discriminator — the
        # `build` vs `rebuild` shape `corpus.excluded` already paid for once.
        (
            "a test path is a COMPONENT, never a substring",
            {
                p: fixture_file(p)
                for p in (
                    "tests/test_x.py",
                    "a/tests/b.py",
                    "scratch/foo_selftest.py",
                    "contests/runner.py",
                    "scratch/latest_run.py",
                    "scratch/tsdbprobe.py",
                )
            },
            {
                "tests/test_x.py": True,
                "a/tests/b.py": True,
                "scratch/foo_selftest.py": True,
                "contests/runner.py": False,
                "scratch/latest_run.py": False,
                "scratch/tsdbprobe.py": False,
            },
        ),
        _provenance_fixture(),
    ]


def _cases_index() -> list[tuple[str, object, object]]:
    """Pin that the call INDEX answers exactly what the per-slot corpus sweep answered.

    ⚑ SPLIT OUT BECAUSE THE PER-FILE GATE SAID SO, and the gate read the shape correctly:
    these pin a claim about the walk's COST STRUCTURE, distinct from the reach/join/cycle
    cases around them. The two arms are the two ways a cost fix becomes a wrong answer.

    ⚑⚑⚑ THE FIRST ARM PINS THAT `binds` IS STILL APPLIED AT LOOKUP. The index is keyed on the
    callee NAME alone, because reachability depends on the DEFINING module and so varies per
    query. Folding it into the key would make the index answer a narrower question than the
    one asked — and a foreign witness does not merely add noise: it can AGREE and yield a
    confident wrong type carrying a `file:line` that reads as proof. So the defining module's
    own call must count and a stranger's same-named call must not.

    ⚑⚑⚑ THE SECOND PINS THAT AN INDEX NOBODY QUERIES NEVER WALKS THE CORPUS, and it exists
    because the first cut FAILED it. An index built in `__init__` charges every walk one full
    sweep whether or not a slot needs one — so a FULLY ANNOTATED module, whose slots all
    return STATED before any call site is consulted, pays for a scan it never uses.
    `iface_cost --selftest` measures exactly that as "a fully annotated module sweeps the
    corpus zero times", and it went red. The eager index taxed precisely the annotated
    modules the surrounding arc exists to produce: a cost fix that regressed the good case
    while improving the bad one, caught only because another module's suite asked.
    """
    src = 'def f(a):\n    return 1\nf("x")\n'
    home = from_source(src, "scripts/idx_home.py")
    if home is None:
        raise TypeError(src)
    unused = CallIndex([str(Path(home.path).absolute())])
    # ⚑⚑ THE FIXTURES ARE WRITTEN TO DISK, and the first cut's failure is why. `CallIndex`
    # populates itself through `load`, which READS FILES — so an in-memory path name indexes
    # to nothing, and a "stranger contributes 0" arm passed while measuring an EMPTY index
    # rather than a rejected witness. A case that cannot distinguish those two is green for
    # the wrong reason, which is the discriminator-in-name-only shape this suite refuses.
    tmp = Path(__file__).absolute().parent / "_index_fixture"
    names = {"ix_stranger.py": "f(3)\n", "ix_importer.py": "from idx_home import f\nf(3)\n"}
    tmp.mkdir(exist_ok=True)
    try:
        for name, text in names.items():
            (tmp / name).write_text(text, encoding="utf-8")
        paths = [str(tmp / n) for n in names]
        # ⚑⚑ THE ARMS MEASURE THE INDEX'S *CONTRIBUTION*, NOT THE TOTAL, and the first cut
        # compared totals and failed for that reason alone. `sites` always prepends
        # `calls_in(here, ...)` — the defining module's own calls, which no index supplies —
        # so a raw total carries that baseline into every arm and a correct rejection reads
        # as an off-by-one. Subtracting the `own` baseline asks the question the case means.
        own = len(CallIndex([]).sites("f", home))
        reach = {
            "own": own,
            "stranger": len(CallIndex([paths[0]]).sites("f", home)) - own,
            "importer": len(CallIndex([paths[1]]).sites("f", home)) - own,
        }
    finally:
        for name in names:
            (tmp / name).unlink(missing_ok=True)
        tmp.rmdir()
    return [
        # ⚑ ALL THREE DIRECTIONS AT ONCE: the defining module's own call counts, a STRANGER
        # calling a same-named `f` does not, and a module that IMPORTS the def does. A lookup
        # that dropped `binds` passes the first and third and fails the second; one that
        # rejected everything foreign passes the first two and fails the third. Neither can
        # be green by accident, and an EMPTY index fails the third.
        (
            "the index applies binds at LOOKUP, never folding it into the key",
            reach,
            {"own": 1, "stranger": 0, "importer": 1},
        ),
        ("an index nobody queries never walks the corpus", unused.walked, False),
    ]


if __name__ == "__main__":
    sys.exit(main(sys.argv))
