# SPDX-License-Identifier:Apache-2.0
# Copyright 2026 Mike Mol
"""Corpus-wide censuses: `pycodemod`'s whole-tree questions.

⚑ THE SEAM IS THE UNIT OF THE ANSWER, NOT THE TOPIC.  Everything here answers
about the CORPUS — how big are the modules (`--size`), what state do they hold
(`--state`), what do they import and does it cross a declared boundary
(`--imports`, `--crossings`), which of them read build artifacts (`--artifacts`),
which are paperkit projects (`--projects`), what does mypy say (`--types`).  The
name-query modes that stayed behind (`--calls`, `--dead`, `--source`, `--attr`,
`--key`, `--rivals`) take an IDENTIFIER and answer about it; these take no
operand and answer about the tree.  That is a difference in the shape of the
question, which is why it is a stable boundary rather than a topical one.

⚑ THE MEMO TABLES TRAVEL WITH THEIR READERS.  `_IMPORTS_CACHE`, `_PARSE_CACHE`,
`_SCHEMA`, `_DERIVER`, `OVERLARGE_LINES`, `FAILURE_BEARING` / `SUCCESS_ONLY` and
`ROUTE` are each read by exactly one census in this file; leaving them behind
would have split a memo from the only thing that consults it — the shape
`--state` exists to detect.

⚑ THE ⚑ BLOCKS MOVED VERBATIM WITH THEIR FUNCTIONS, by CST transform rather than
by hand.  `FAILURE_BEARING`/`SUCCESS_ONLY` in particular record WHY the artifact
census splits on whether an artifact can carry a failure — a tool reading failure
records emits commit-blockers by construction — and that reasoning is the half
worth more than the code.

⚑ `ROOT` IS READ AS `_c.ROOT`, NEVER `from … import ROOT`.  `corpus.__enter__`
rebinds it so `--archive` / `--in` swap the corpus under every mode; a snapshot
binding would leave these censuses answering about the main tree while the rest
of the tool answered about the archive — silently.  Verified live: `--in
persistqueue --dead` reports 194 defs from the package, not from this repo.
"""
import ast
import functools
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




def type_errors(paths=None):
    """{`<code>::<relpath>` -> [messages]} — the mypy census, ratchet-keyed.

    ⚑ WHY A TYPE GATE, AND THE EVIDENCE IS THIS SESSION'S OWN DEFECT LOG (user,
    2026-08-01: *"have we reached a point where we should be using [a type checker]
    to provide typing guarantees… because that's what it's feeling like"*).  Seven
    defects in one session that a checker catches mechanically:

      · `log_is_fresh` widened 2-tuple → 3-tuple; 4 returns and 1 call site
        unchecked (the bug being debugged when this was proposed)
      · `_classify` called before it existed — §55, *"the FOURTH invented API this
        session"*, and I was already counting them
      · `AL.agda_files` — an alias that does not exist (§65)
      · `CII.importers()` — an invented API (§49)
      · `agda_lex.imports_of` behind a `hasattr` fallback (§52) — **the strongest
        case: the guard HID it, and a fallback to an absent function would have
        measured NOTHING**
      · `group_statements(lines, [])` where a CALLABLE was required (§58c)
      · an unused `subprocess as _sp` import (§66)

    Every one cost a run-edit-run cycle; two shipped behind guards that silently
    degraded.  *A signature change verified only by running it is the same class as
    a census verified only by reading it.*

    ⚑ KEYED `<error-code>::<relpath>`, NOT COUNTED.  `ratchet.set_ratchet` needs a
    SET so swap-gaming is refused (remove one, add another — the added key is
    caught) and so `--list` can enumerate.  Line numbers are deliberately NOT in
    the key: they churn on every unrelated edit above a site, which is §7g's
    measured defect (`check_rederive_ratchet` keyed on line number and would have
    fired on nearly every commit).

    ⚑ AND `--ignore-missing-imports` IS NOT A CONCESSION.  These tools import
    `panflute`, `libcst`, `cupy` — optional deps absent in a bare environment.
    Without it the census would be dominated by rows that say nothing about our
    code, which is the noise failure §63/§64 keep recording: *a census too wide to
    read has already failed.*
    """
    import subprocess
    files = [os.path.relpath(p, _pycodemod_core.ROOT) for p in (paths or _pycodemod_core.py_files())]
    # ⚑ `sys.executable`, NOT `"python3"` — AND THE FIRST CUT MEASURED NOTHING.
    # Under `uv run --with mypy`, mypy is installed for THAT interpreter; a bare
    # `python3` subprocess is a different one, so the run failed and the parse
    # found no error lines: **0 keys over 60 unannotated files**, reported as a
    # clean census.  That is the guard-degrades-to-measuring-nothing class (§52) in
    # the tool built to catch it, caught only because zero was implausible.
    try:
        p = subprocess.run(
            # ⚑ `--explicit-package-bases` BECAUSE THE CORPUS HAS DUPLICATE
            # BASENAMES.  MEASURED: `scratch/hadamard_basis.py` and
            # `scratch/figures/hadamard_basis.py` both map to module
            # `hadamard_basis`, and mypy REFUSES the whole run rather than guess —
            # correctly.  Without this the census is not "clean", it is ABSENT, and
            # my first cut reported that absence as `0 keys`.
            [sys.executable, "-m", "mypy", "--ignore-missing-imports",
             "--explicit-package-bases", "--no-error-summary",
             "--no-color-output", "--"] + files,
            cwd=_pycodemod_core.ROOT, capture_output=True, text=True, timeout=900)
    except FileNotFoundError:
        return None
    # ⚑ AND A FAILED RUN MUST NOT READ AS A CLEAN ONE.  mypy exits 1 when it finds
    # errors and 2 when it CANNOT RUN; only the first is a census.  Returning None
    # for the second is what makes "no errors" mean no errors.
    if p.returncode not in (0, 1) or "No module named mypy" in (p.stderr or ""):
        # ⚑ SAY WHY IT COULD NOT RUN.  "not importable" was my guess printed as a
        # fact; mypy exits 2 for a config error, a duplicate module name, or an
        # unreadable path just as readily as for an absent install — and each wants
        # a different fix.  Carry the real message rather than a plausible story.
        return {"__unrunnable__": [(p.stderr or p.stdout or "").strip()[:400]
                                   or f"mypy exited {p.returncode}"]}
    out = {}
    for line in (p.stdout or "").splitlines():
        m = re.match(r"^(.+?):\d+:(?:\d+:)?\s*error:\s*(.*?)(?:\s*\[([\w-]+)\])?$",
                     line)
        if not m:
            continue
        rel, msg, code = m.group(1), m.group(2), m.group(3) or "misc"
        out.setdefault(f"{code}::{rel}", []).append(msg)
    return out


# ⚑ THE BUILD-ARTIFACT VOCABULARY, SPLIT BY WHETHER A FAILURE CAN APPEAR IN IT.
# This is the whole discriminator, so it is stated as data rather than buried in a
# predicate: an artifact either CAN carry a record of a module that did not compile,
# or it structurally cannot.
#
#   * `.agdai.log`  — `gen_build_makefiles:262-274` writes one per module and `cat`s
#     it to stderr on failure.  It is where a typecheck error LIVES.
#   * make's own output — `*** [<mod>.agdai] Error` is the build's verdict on itself,
#     and §53 measured it naming 121 failures where the log-derived count saw 41
#     (a FAILED module leaves no fresh log, so artifacts alone undercount 3x).
#   * `.agda-times.tsv` / `.agda-profile.tsv` — membudget and proofcost record ONLY
#     SUCCESSFUL compiles (CLAUDE.md states it: "a failed/OOM-killed run is not
#     representative").  A failure cannot appear in these BY CONSTRUCTION.
#
# The distinction is not a judgement about intent — it is a property of what the
# producing writer will and will not put in the file.
# ⚑ AND `.agdai` IS A SUCCESS ARTIFACT, NOT A FAILURE ONE — my first vocabulary
# put it in FAILURE_BEARING and the census read 49-of-52, which is the answer a
# non-discriminating predicate always gives.  A `.agdai` is a COMPILED CORE: it
# exists only because the module typechecked, exactly like `.agda-times.tsv`
# exists only for a successful compile.  I admitted it by prefix-similarity to
# `.agdai.log`, which is the guard-written-from-the-instance shape (the `stale`
# vs `blocked` conflation of §54, one layer up).  The suffix is one character;
# the polarity is opposite.
FAILURE_BEARING = (".agdai.log", "isolate_check", "[FileNotFound]",
                   "[NotInScope]", "error:", "*** [")
SUCCESS_ONLY = (".agdai", ".agda-times.tsv", ".agda-profile.tsv",
                "peak_mb", "maxrss")


def _l2_cached(consumer, key_fn):
    """`shared_cache.cached`, resolved LAZILY — stacked UNDER `lru_cache`.

    ⚑ THE DECORATOR, NOT A HAND-ROLLED ADAPTER (user, 2026-08-04: *"the decorator
    pattern would deal with a LOT of the boilerplate"*).  My first version of the
    L2 wiring in this file was a `_shared_l2()` resolver plus per-site
    fetch/store/write-back blocks — the same ~40 lines `agda_lex` had grown as a
    class, and ~1,100 across the 28 censused sites.  Stacking says it in two
    lines and puts L1 in front by construction:

        @functools.lru_cache(maxsize=N)         # L1 — a hit never hits the wire
        @_l2_cached(consumer, key_fn)           # L2 — only on an L1 miss
        def derive(...): ...

    ⚑ LAZY AND IDENTITY-ON-FAILURE: this module is imported by gates and pool
    children, so dialling a socket at import time would make the network a
    dependency of LOADING a tool that may never consult the cache.  Absent
    module, or `SUBSTRATE_NO_CACHE`, degrades to calling straight through."""
    def deco(fn):
        bound = []

        def wrapper(*a, **k):
            if not bound:
                if os.environ.get("SUBSTRATE_NO_CACHE"):
                    bound.append(fn)
                else:
                    try:
                        sys.path.insert(
                            0, os.path.dirname(os.path.abspath(__file__)))
                        import shared_cache as _sc
                        bound.append(_sc.cached(consumer, key_fn)(fn))
                    except Exception:
                        bound.append(fn)
            return bound[0](*a, **k)
        wrapper.__name__ = getattr(fn, "__name__", "l2")
        wrapper.__doc__ = getattr(fn, "__doc__", None)
        wrapper.__wrapped__ = fn
        return wrapper
    return deco


def _corpus_key(files):
    """Key material for a whole-corpus derivation — delegated, not re-derived."""
    try:
        sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
        import shared_cache as _sc
        return _sc.corpus_key(files)
    except Exception:
        return None


def build_artifact_readers(paths=None):
    """[(relpath, [artifact...], bearing)] — which tools READ build artifacts.

    ⚑ MEMOISED, BECAUSE THE CALLER'S QUESTION IS PER-ITEM AND THIS ANSWER IS
    PER-CORPUS.  `worklist_gate.gates_reached` runs once per worklist item; an
    unmemoised call re-parsed every tool with libcst each time and took `--next`
    from 57s past 120s.  That is §55's finding — *before reaching for
    concurrency, check whether the work is REPEATED* — reproduced by me in the
    same edit whose comment cites it.  Keyed on the resolved path set, so a
    scoped run and a full sweep do not share an entry.

    ⚑ A TOOL THAT READS BUILD FAILURE RECORDS IS, BY CONSTRUCTION, A PRODUCER OF
    COMMIT-BLOCKERS (user, 2026-08-03: *"anything that generates rows from reading
    build logs INTRINSICALLY surfaces rows which block make, which intrinsically
    blocks the commit"*).  That is a discovery rule over TOOLS, not a lookup per
    row: classify once at the source and every row the tool emits inherits it.

    ⚑ WHY THIS IS NOT A SECOND ROUTE TO AN EXISTING FACT.  `worklist_gate.
    gates_reached` walks the ITEM graph hunting a `.py` gate node, finds none for a
    build-derived row, and reports leverage -1.  Teaching `gate_status.gates()` to
    parse the hook's `make -C agda -j` line would mint a SECOND, independently
    computed answer to "does this block the commit" — the derived-view divergence
    (§6) this arc has now paid for four times.  The provenance already carries it;
    this reads the provenance.

    ⚑ AND THE SPLIT IS REPORTED, NOT ASSUMED.  The predicate could have been
    written as "reads failure records" directly, which would return a smaller set
    and hide its own discrimination.  Returning the artifact list per tool makes
    the division VISIBLE: if a tool reads both kinds, or if the two populations do
    not separate, that is in the output rather than in my reading of it.  Same
    reason `--discards` reports rows and `writes_by_default` reports `why`.

    `bearing` is one of:
      FAILURE  — reads an artifact that can hold a compile failure  -> blocker source
      SUCCESS  — reads only success-recorded artifacts (timings, peaks) -> not
      BOTH     — reads both kinds; the row names which, and it is not a tie
    """
    # ⚑ THE CACHING IS ON `_artifact_readers`, NOT HERE.  This wrapper exists only
    # to normalise the argument into something hashable, because `lru_cache` keys
    # on the argument tuple and a list is not hashable.  Everything else — the L1
    # cap, the L2 round trip, the key discipline — rides on the decorator stack.
    return _artifact_readers(tuple(sorted(paths or _pycodemod_core.py_files())))


@functools.lru_cache(maxsize=16)
@_l2_cached("pycodemod.artifacts", lambda files: _corpus_key(files))
def _artifact_readers(files):
    """The derivation — see `build_artifact_readers` for what it computes.

    ⚑ THE L1 AND L2 KEYS ARE DIFFERENT, AND THAT IS THE POINT.  `lru_cache` keys
    on the PATH SET, which is exact within one process — the files cannot change
    under it.  That same key is STALE-ON-EDIT the moment an entry outlives the
    run, so promoting it to a shared store unchanged would serve a pre-edit
    answer to a post-edit question, which is worse than not caching at all.
    `_corpus_key` carries each file's (path, size, mtime_ns), so an edit misses
    by construction.

    ⚑ AND THE HAND-ROLLED DICT IS GONE.  `_ARTIFACT_CACHE` was a module dict plus
    a `tuple(sorted(...))` key plus a membership test plus a write-back — four
    lines reimplementing `lru_cache`, in the file whose own census flagged 28
    such caches.  Same conversion as `agda_lex.mask_comments`; same reason."""
    files = list(files)
    out = []
    for p in files:
        try:
            src = open(p, encoding="utf-8").read()
        except OSError:
            continue
        # ⚑ COMMENTS AND DOCSTRINGS ARE NOT READS — the discrimination that makes
        # every mode here beat grep.  This module's own FAILURE_BEARING tuple and
        # the ⚑ block above would otherwise make `pycodemod.py` its own top hit.
        if cst is None:
            continue
        try:
            tree = cst.parse_module(src)
        except Exception:
            continue

        class _V(cst.CSTVisitor):
            """⚑ A DOCSTRING IS A STRING LITERAL, and counting it as a read makes
            every tool that DISCUSSES an artifact look like one that consumes it.
            This module's own vocabulary block named `.agdai.log` six times and
            became the corpus's top hit — the same prose-vs-code discrimination
            that makes `--calls` beat grep, at the literal layer.  A docstring is
            the sole expression of an `Expr` statement; an artifact token is an
            operand."""

            def __init__(self):
                self.lits = []
                self.docstrings = set()

            def visit_Expr(self, node):
                if isinstance(node.value, cst.SimpleString):
                    v = node.value.evaluated_value
                    if isinstance(v, str):
                        self.docstrings.add(id(node.value))

            def visit_SimpleString(self, node):
                if id(node) in self.docstrings:
                    return
                v = node.evaluated_value
                if isinstance(v, str) and v and len(v) < 80 and "\n" not in v:
                    self.lits.append(v)

        v = _V()
        tree.visit(v)
        # ⚑ `".agdai" in ".agdai.log"` IS TRUE, so a substring test makes every
        # FAILURE reader also a SUCCESS reader and the verdict collapses to BOTH.
        # The two markers that carry the whole discrimination differ by a SUFFIX,
        # and one is a PREFIX OF THE OTHER — so the failure vocabulary is matched
        # FIRST and its matches are subtracted before the success pass.  I wrote
        # the warning about this pair one edit earlier and then walked into it
        # from the other side; the cases are what caught it.
        fail = sorted({a for a in FAILURE_BEARING
                       for s in v.lits if a in s})
        matched_fail = {s for s in v.lits
                        if any(a in s for a in FAILURE_BEARING)}
        succ = sorted({a for a in SUCCESS_ONLY
                       for s in v.lits
                       if s not in matched_fail and a.lower() in s.lower()})
        if not fail and not succ:
            continue
        bearing = ("BOTH" if fail and succ else "FAILURE" if fail else "SUCCESS")
        out.append((os.path.relpath(p, _pycodemod_core.ROOT), fail + succ, bearing))
    return sorted(out)


def _code_lines(src):
    """The 1-based line numbers that are CODE — not comment, not docstring.

    ⚑ TOKENIZE, DO NOT GUESS.  A `#` inside a string is not a comment and a
    triple-quote inside a comment is not a docstring; `tokenize` already knows
    both, and re-deriving it with a regex is how the `-->`-is-a-name class got
    into `agda_lex` (a stripper that was right about the common case)."""
    import io
    import tokenize as _tk
    comment, strings = set(), set()
    try:
        for tok in _tk.generate_tokens(io.StringIO(src).readline):
            if tok.type == _tk.COMMENT:
                comment.add(tok.start[0])
            elif tok.type == _tk.STRING:
                # a STRING token spanning lines covers all of them
                for ln in range(tok.start[0], tok.end[0] + 1):
                    strings.add(ln)
    except Exception:
        # a file that will not tokenize gets the permissive answer: every line is
        # code.  Refusing to report would make a syntax error look like a clean
        # scan, which is the absence-as-finding shape.
        return set(range(1, src.count("\n") + 2))
    out = set()
    for i, line in enumerate(src.splitlines(), 1):
        if not line.strip():
            continue
        # ⚑ A LINE HOLDING ONLY A COMMENT OR ONLY STRING IS NOT CODE.  A line with
        # code AND a trailing comment IS code — dropping it would hide a defect
        # that happens to carry an explanation.
        if i in comment and line.strip().startswith("#"):
            continue
        if i in strings and not line.strip().startswith(("#",)):
            # keep it only if there is code outside the string on this line
            stripped = re.sub(r'("""|\'\'\'|"[^"]*"|\'[^\']*\')', "", line).strip()
            if not stripped or stripped in ("(", ")", ",", "):"):
                continue
        out.add(i)
    return out


def writes_by_default(path):
    """(bool, why) — does a BARE invocation of this tool write a real file?

    ⚑ THE QUESTION A DIAGNOSTIC MUST ASK BEFORE IT RUNS SOMETHING.  `gate_status
    --modes` runs a tool once per flag mode to compare their behaviour; on
    `sppf_node_index.py` that REGENERATED the artifact three times, because that
    tool's module body runs at import and its final `else:` writes.  The output was
    idempotent so nothing was lost — but a sweep multiplies one accidental write by
    the number of modes, which is the `prune_imports` write-polarity hazard (§7e)
    in the worst possible place.

    ⚑ DISCOVERED, NOT DECLARED — an allow-list would rot exactly as the four
    `agda_files()` bodies did.  A write is "guarded" when it is reachable only
    under an explicit opt-in (`--apply`), or is inert (`--check` compares), or
    targets a tempfile.  Anything else writes on a bare run.

    Deliberately CONSERVATIVE: it answers "could a bare run write", so a tool whose
    write sits behind a runtime condition this cannot see reads as write-default.
    For a guard that decides whether to RUN something, a false "yes" costs one
    skipped mode; a false "no" costs an unintended write.  That asymmetry is the
    same one `prune_imports.should_keep` records — and it points the other way here,
    because the risky act is writing, not skipping.
    """
    try:
        src = open(path, encoding="utf-8").read()
    except OSError as e:
        return False, f"unreadable: {e}"
    if cst is None:
        return False, "libcst not importable"
    hits = []
    for i, line in enumerate(src.splitlines(), 1):
        if not re.search(r'open\([^)]*["\'][wa]', line):
            continue
        hits.append((i, line.strip()))
    if not hits:
        return False, "no write call"
    # a write is INERT if the whole file gates on --apply, or if every write's
    # target is a tempfile, or the write sits inside the selftest
    st = re.search(r'^def _selftest\(', src, re.M)
    st_line = src[:st.start()].count("\n") + 1 if st else None
    live = []
    # ⚑ THE TEMPFILE TEST IS ABOUT THE TARGET VARIABLE, NOT THE WRITE LINE.
    # My first cut looked for "tempfile" IN the write line, but the idiom binds the
    # path one line earlier (`tf = os.path.join(tempfile.mkdtemp(), …)` then
    # `open(tf,"w")`), so it matched nothing and every tempfile writer read as
    # write-default.  Resolve the variable to its binding, the same
    # positional-not-file-level correction as everywhere else in this arc.
    tmpvars = set(re.findall(
        r'(\w+)\s*=\s*[^\n]*(?:tempfile\.|mkdtemp\(|mkstemp\()', src))
    for ln, text in hits:
        if st_line and ln >= st_line:
            continue                      # a fixture, not a write path
        m = re.search(r'open\(\s*(\w+)', text)
        if m and m.group(1) in tmpvars:
            continue
        if "tempfile" in text or "mkdtemp" in text or "mkstemp" in text:
            continue
        live.append((ln, text))
    if not live:
        return False, "writes only fixtures/tempfiles"
    if re.search(r'["\']--apply["\']', src):
        return False, "gated on --apply"
    return True, f"unguarded write at line {live[0][0]}"


def discriminates(path, mutators=None):
    """[(mutator, verdict, detail)] — does this module's `_selftest` actually DISCRIMINATE?

    ⚑ THE QUESTION THE ARC KEPT ANSWERING BY HAND, AND GOT WRONG (user, 2026-08-01:
    *"if you have a question the tooling doesn't answer directly, fix the tooling"*).
    A selftest that passes proves the code passes ITS OWN cases; it does not prove a
    case would FAIL against the defect it names.  Measured instances, all this arc:

      · §7b-bis — a class-guard test matched the literal spelling just fixed, so the
        survivors never matched; **verified False on the live file, would have passed
        forever**.
      · §6c — an `@expectedFailure` compared two regexes IT DEFINED ITSELF, so it
        could pass while the gate stayed broken.
      · §60 — `check_snapshot_guard`'s selftest re-implemented the predicate rather
        than driving it, and stayed green at 5/5 through a real false positive.
      · §63 — `mdstruct` returned `True` at `0/0`; an absent dependency scored as a
        green suite.

    Each was caught by writing a THROWAWAY SCRIPT that simulated the defect — which is
    reasoning-not-codified, and is why this is a command.

    THE METHOD: mutate the module's source in a way the case CLAIMS to catch, re-import
    it in a fresh namespace, and run its `_selftest`.  A case-set that still passes is
    NOT DISCRIMINATING — it is decoration.  Verdicts:

      · `DISCRIMINATES` — the mutant fails the suite (the cases bind)
      · `BLIND`         — the mutant PASSES (the suite cannot see this defect)
      · `n/a`           — the mutation did not apply to this source

    ⚑ A `BLIND` VERDICT IS NOT AUTOMATICALLY A DEFECT.  A mutator names one specific
    defect class; a suite may legitimately not cover it (the class may be out of scope,
    or guarded elsewhere).  What it is NOT is evidence of coverage — and reading a green
    suite as coverage is exactly the failure above.  Report the pair, never a bare bit.

    ⚑ AND THE MUTATORS ARE THE ARC'S OWN MEASURED DEFECT CLASSES, not invented ones —
    each `(name, pattern, replacement)` is a real bug this repo shipped.
    """
    MUT = mutators if mutators is not None else [
        # §52 — the guard that degrades to measuring NOTHING.  `imports_of` behind a
        # `hasattr` fallback to an empty set reduced a freshness check to "newer than
        # its own source" and reported 2802-of-2810 clean on a broken tree.
        ("sentinel-read-as-clean",
         re.compile(r'if\s+rows\s+is\s+None\s+or\s+"__unrunnable__"[^\n]*:'),
         'if False:'),
        # §7g — a ratchet key that moves when an unrelated line moves.
        ("key-gains-a-line-number",
         re.compile(r'(f"\{code\}::\{rel\}")'), r'f"{code}::{rel}:{1}"'),
        # §60/§63 — an empty census reported as a pass rather than as UNMEASURED.
        ("empty-census-passes",
         re.compile(r'^(\s*)return ratchet\.set_ratchet\(', re.M),
         r'\1return 0  # mutant\n\1return ratchet.set_ratchet('),
        # §6d — scope restated instead of imported: a future promotion escapes silently.
        ("scope-hardcoded",
         re.compile(r'^POPULATION = .*$', re.M),
         'POPULATION = ["scripts"]'),
        # 2026-08-05 — RAM-AS-STORAGE: a streaming cursor materialized back into a
        # list.  `catalog_query._rows` did `.fetchall()` over a 3.3GB store, and the
        # consequence is not only memory: `cmd_sql` read its header off `rows[0]` and
        # then re-walked, which a LIST tolerates and a CURSOR does not — the header
        # read consumes row one and it vanishes from the output.  A suite that only
        # checks values, never single-passness, passes both ways.
        ("stream-materialized",
         re.compile(r'return con\.execute\(q, args\)\s*$', re.M),
         'return con.execute(q, args).fetchall()'),
    ]
    try:
        src = open(path, encoding="utf-8").read()
    except OSError as e:
        return [("<unreadable>", "n/a", str(e))]
    if not re.search(r'^def _selftest\(', src, re.M):
        return [("<no _selftest>", "n/a", "module defines no _selftest")]

    import importlib.util, io, contextlib, tempfile as _tf
    out = []
    for name, pat, rep in MUT:
        mutated, n = pat.subn(rep, src, count=1)
        if not n:
            out.append((name, "n/a", "mutation does not apply to this source"))
            continue
        # ⚑ WRITE THE MUTANT BESIDE THE ORIGINAL, NOT INTO A TEMPDIR.  A module resolves
        # its siblings from `__file__` (`sys.path.insert(0, dirname(__file__))`, the idiom
        # in every gate here), so a mutant loaded from /tmp fails to import its own
        # authorities and raises `ModuleNotFoundError` — which this harness would then
        # score as DISCRIMINATES.  MEASURED: all three mutators returned that, and every
        # verdict was an artifact of the harness rather than of the suite.  Same class as
        # §30's five bad fixtures: a fixture that never exercised its hypothesis, read as
        # a result.  The mutant is named `.mutant-<pid>-…` and deleted in `finally`.
        mp = os.path.join(os.path.dirname(path),
                          f".mutant-{os.getpid()}-{re.sub(r'\W', '_', name)}.py")
        with open(mp, "w", encoding="utf-8") as fh:
            fh.write(mutated)
        spec = importlib.util.spec_from_file_location(
            "mut_" + re.sub(r'\W', '_', name), mp)
        mod = importlib.util.module_from_spec(spec)
        buf = io.StringIO()
        try:
            try:
                with contextlib.redirect_stdout(buf), contextlib.redirect_stderr(buf):
                    spec.loader.exec_module(mod)
                    rc = mod._selftest()
            except (ImportError, SyntaxError) as e:
                # ⚑ A MUTANT THAT CANNOT LOAD MEASURED NOTHING — REFUSE, never score.
                # This is the arc's own guard-degrades class (§52) turned on this
                # harness: an import failure is a fact about the HARNESS (wrong load
                # path, a mutation that broke syntax), not about the suite, and
                # reading it as DISCRIMINATES manufactures coverage out of an error.
                out.append((name, "n/a",
                            f"mutant did not run: {type(e).__name__}: {e}"))
                continue
            except BaseException as e:
                # a mutant that loads and then RAISES from the suite is genuinely
                # caught — by the interpreter rather than by a case, but the defect
                # still cannot ship silently
                out.append((name, "DISCRIMINATES",
                            f"suite raises {type(e).__name__}"))
                continue
        finally:
            try:
                os.unlink(mp)
            except OSError:
                pass
        text = buf.getvalue()
        fails = [l.strip() for l in text.splitlines() if l.strip().startswith("FAIL")]
        # ⚑ THE VERDICT WAS `rc != 0`, WHICH SCORES EVERY BOOL-RETURNING SUITE AS
        # BLIND (2026-08-05).  `_selftest` returns a BOOL here — the convention in
        # this repo — and `False != 0` is **False** in Python, so a suite that
        # caught the mutant perfectly was reported as not covering it.  Measured on
        # `catalog_query`: the row read `BLIND` while its own detail column showed
        # `FAIL _rows returns a stream`, i.e. the verdict contradicted the evidence
        # printed beside it.  A truthiness test is the honest predicate for a
        # convention that admits both `0`/`1` and `False`/`True`, and the FAIL lines
        # are corroborating evidence either way.
        # ⚑ AND MY FIRST FIX FOR THAT WAS TOO LOOSE, CAUGHT BY THE SWEEP'S OWN
        # OUTPUT: `(not rc) or fails` scored `check_rederive_ratchet` and
        # `check_snapshot_guard` as `ok` on rows whose DETAIL read *"suite PASSES
        # the mutant — not covered"*.  Those suites return a falsy `rc` in their
        # ordinary REFUSING state, which has nothing to do with the mutation — so
        # `rc` alone cannot separate "this case caught the mutant" from "this
        # module was already unhappy".  A printed FAIL line is the only evidence
        # that a CASE fired, so it is the predicate; `rc` is corroboration only
        # when the suite reports no failures at all and still returns success.
        #
        # ⚑ The tell was the row contradicting its own detail column — the same
        # shape as the BLIND-with-a-FAIL-line row one edit earlier.  A verdict
        # and its evidence disagreeing is the cheapest available signal that the
        # verdict is computed wrong; twice in one sitting, in opposite directions.
        caught = bool(fails)
        out.append((name,
                    "DISCRIMINATES" if caught else "BLIND",
                    (fails[0][:80] if fails else "suite PASSES the mutant — not covered")))
    return out


_IMPORTS_CACHE = {}


def imports(paths=None):
    """[(top_module, verdict, n_files, example)] — what the CORPUS actually imports.

    ⚑ `--available` ANSWERS ABOUT NAMES I SUPPLY, WHICH IS THE FROZEN-ROSTER SHAPE
    ONE LEVEL UP (user, 2026-08-02: *"worth scanning over the entire repo to find
    the things which the various scripts and tools import"*).  I wrote this repo's
    first `pyproject.toml` from FOUR dependencies I happened to remember, which is
    exactly how `run_selftests.DIRS` and this module's own `_roots` went stale --
    a hand-listed population can only be as current as its last edit.  The
    dependency set is DISCOVERABLE from the source; asking me to recall it is the
    judgement-not-in-code shape.

    ⚑ THE VERDICT IS FOUR-WAY, NEVER present/absent.  Those four are different
    facts with different remedies, and collapsing them is what hid the real state:
      * STDLIB     -- no declaration owed;
      * DECLARED   -- in pyproject, importable: the healthy case;
      * UNDECLARED -- importable but in NO manifest.  It works today and breaks on
                      a fresh clone.  `libcst` and `networkx` were BOTH in this
                      state while backing the losslessness gate and the DAG
                      authority;
      * MISSING    -- imported and NOT importable.  `panflute` and `mypy` were
                      here, and `mypy` backs a WIRED PRE-COMMIT GATE, so a green
                      hook run was proving less than it appeared to.

    ⚑ AND THE FIRST-PARTY MODULES ARE EXCLUDED BY MEASUREMENT, NOT BY A LIST.  A
    sibling tool (`import agda_lex`) is not a dependency; the test is whether the
    name resolves to a file inside this repo.  An allow-list of our own module
    names would rot the moment a tool is added -- the defect this docstring's own
    first paragraph is about.
    """
    import sysconfig
    stdlib_dir = sysconfig.get_paths().get("stdlib", "")
    files = paths or _pycodemod_core.py_files()
    # ⚑ MEMOISED — `worklist_gate --order` CALLED THIS FOUR TIMES FOR 58s OF A 209s RUN.
    # It AST-parses the whole Python corpus; four callers each asked independently and
    # each paid in full.  Same class as `_blast_radius` re-running `parse_tree()` per
    # query (§55: 300s -> 2.7s) and `log_is_fresh` globbing per call (381s -> 81s):
    # the work was REPEATED, not large, so concurrency would have run four copies of
    # the same waste.  Keyed on the resolved file set, so a different scope is a
    # different answer rather than a stale hit.
    _key = tuple(sorted(str(f) for f in files))
    _hit = _IMPORTS_CACHE.get(_key)
    if _hit is not None:
        return _hit
    seen = {}                        # top-level name -> [files]
    for p in files:
        try:
            with open(p, encoding="utf-8", errors="replace") as fh:
                src = fh.read()
            # ⚑ `filename=` IS THE ATTRIBUTION, not decoration: without it every
            # diagnostic this corpus-wide sweep raises reads `<unknown>:<line>`,
            # and the tool that parsed every .py file in the repo cannot say
            # WHICH one it is complaining about (cost one stack-hook hunt).
            tree = ast.parse(src, filename=str(p))
        except SyntaxError:
            continue
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                names = [a.name for a in node.names]
            elif isinstance(node, ast.ImportFrom):
                # a RELATIVE import names no external package
                if node.level or not node.module:
                    continue
                names = [node.module]
            else:
                continue
            for n in names:
                seen.setdefault(n.split(".")[0], []).append(p)

    # ⚑ FIRST-PARTY IS DECIDED BY THE TREE, NOT BY `find_spec`, AND MY FIRST CUT
    # GOT 124 ROWS WRONG.  These tools import each other via `sys.path` insertion
    # (`import ratchet`, `import items`, `import jea_core`), so they are NOT
    # importable from here -- `find_spec` raises, the row falls to MISSING before
    # any origin test runs, and a sibling tool reads as a missing dependency.  A
    # false positive of that size would poison any gate built on this census.  The
    # honest test is whether a file of that name EXISTS in the corpus.
    ours = set()
    for p in files:
        base = os.path.basename(p)
        if base.endswith(".py"):
            ours.add(base[:-3])
        # a package directory (has __init__.py) is importable by its dir name
        if base == "__init__.py":
            ours.add(os.path.basename(os.path.dirname(p)))
    # vendored subtrees are ours-on-disk too: `scratch/eliza/` is 525 files of
    # third-party source living in-repo, and it is neither a dependency to declare
    # nor stdlib -- it is VENDORED, which is a third answer.
    declared = _declared_deps()
    out = []
    for top, where in sorted(seen.items()):
        if top in ours:
            # ⚑ VENDORED vs OUR OWN: both resolve in-tree, but only one is a
            # third-party copy we would otherwise be declaring.  `vendor/` and a
            # nested package with its own tests are vendored; a flat sibling
            # module is ours.  Reported separately so a reader can tell.
            in_vendor = any("/vendor/" in w or "/eliza/" in w for w in where)
            out.append((top, "VENDORED" if in_vendor else "FIRST-PARTY",
                        len(where), os.path.relpath(sorted(where)[0], _pycodemod_core.ROOT)))
            continue
        try:
            spec = __import__("importlib.util", fromlist=["util"]).find_spec(top)
        except Exception:
            spec = None
        origin = (getattr(spec, "origin", None) or "") if spec else ""
        locs = list(getattr(spec, "submodule_search_locations", None) or []) if spec else []
        # ⚑ A NAMESPACE PACKAGE HAS NO `origin`, AND MY `not origin` BRANCH CALLED
        # THAT STDLIB -- so `opentelemetry` (a namespace package, and a REAL
        # third-party dependency) was reported as part of the standard library.
        # Resolve by WHERE its search locations point, not by the absence of a
        # field.
        probe = origin or (locs[0] if locs else "")
        if spec is None:
            verdict = "MISSING"
        elif origin in ("built-in", "frozen"):
            verdict = "STDLIB"
        elif probe and "site-packages" in probe:
            verdict = "DECLARED" if top in declared else "UNDECLARED"
        elif probe and probe.startswith(_pycodemod_core.ROOT):
            continue                 # resolved into our own tree after all
        elif stdlib_dir and probe.startswith(stdlib_dir):
            verdict = "STDLIB"
        elif not probe:
            verdict = "STDLIB"       # built-in with no file at all
        else:
            verdict = "DECLARED" if top in declared else "UNDECLARED"
        out.append((top, verdict, len(where),
                    os.path.relpath(sorted(where)[0], _pycodemod_core.ROOT)))
    _IMPORTS_CACHE[_key] = out
    return out


def importers(module, paths=None):
    """[(file, line, form, [bound names])] — every file that IMPORTS `module`, and WHAT it reaches.

    ⚑ `--imports` COUNTS AND `--attr <Recv>.*` READS ATTRIBUTES, AND NEITHER ANSWERS
    THE QUESTION A MODULE SPLIT ASKS.  `--imports query_defs` reports `6 file(s)` with
    ONE example — a tally, not the population — and `--attr query_defs.*` reported
    `0 attribute read(s)` because every consumer spells it `from query_defs import q_x`,
    which binds a bare name and never reads an attribute off the module.  So the
    surface a split must re-export was invisible to both modes: the count said six
    files exist and nothing could say which, or which NAMES they take.
    ⚑ THE NAMES ARE THE POINT, NOT THE FILE LIST.  `from m import *` SKIPS a leading
    underscore, so a consumer reading `schema._node` vanishes off a re-export surface
    while every suite stays green — measured here once (`_node`, `_unit`, `_unit_cod`,
    `_orbit_def`).  A `_`-prefixed name in this output is a name a star-re-export
    CANNOT carry and that must therefore be re-imported BY NAME.
    """
    out = []
    for p in (paths or _pycodemod_core.py_files()):
        try:
            with open(p, encoding="utf-8", errors="replace") as fh:
                tree = ast.parse(fh.read(), filename=str(p))
        except (SyntaxError, OSError):
            continue
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for a in node.names:
                    if a.name.split(".")[0] == module:
                        out.append((p, node.lineno, "import",
                                    [a.asname or a.name]))
            elif isinstance(node, ast.ImportFrom) and not node.level:
                if (node.module or "").split(".")[0] == module:
                    out.append((p, node.lineno,
                                "from-*" if any(a.name == "*" for a in node.names)
                                else "from",
                                sorted(a.name for a in node.names)))
    return sorted(out)


def _sibling_modules(path):
    """The `.py` files beside `path` — what an `import x` in it could resolve to locally.

    ⚑ LOCALITY IS A PROPERTY OF THE IMPORTING FILE'S NEIGHBOURHOOD, not of the corpus alone
    and not of the caller's path list. Python resolves a bare `import x` against the importing
    module's own directory first, so that directory IS the locality question's ground truth.
    Deriving it from `py_files()` alone answers about the REPO and misses a fixture; deriving
    it from the scope answers about THE QUESTION and empties itself on a single file.
    """
    try:
        d = os.path.dirname(os.path.abspath(str(path)))
        return [os.path.join(d, fn) for fn in os.listdir(d) if fn.endswith(".py")]
    except OSError:
        return []


def aliases(paths=None, local_only=True):
    """[(file, line, form, module, [bound], scope)] — the BAN-COMPLIANCE census for python imports.

    The `.py` twin of `agda_defs --qualified`.  The agda import ban (⟡ban-decompose) forbids
    `using` / `renaming` / `hiding` / `as` on a Substrate import; the operator's ruling is that
    `from x import y` IS what lacking a bare import looks like in python — it selects names out
    of a module and binds them where the definition site carries `x.y`.  So the compliant form
    is `import x`, used as `x.y`, and the census below grades by FORM:

        import x                  BARE      compliant — takes the module whole, no filter
        import x as q             AS-MOD    relabels the module (agda `import M as Q`)
        from x import y           FROM      selects (agda `open import M using (y)`)
        from x import y as z      FROM-AS   selects AND relabels (agda `renaming`)
        from x import *           FROM-STAR takes all, but binds bare — the re-export shape
        from . import y           RELATIVE  a `from` whose module is positional

    ⚑ BARENESS IS ABOUT THE FILTER, NOT THE QUALIFICATION, and getting that backwards is easy.
    `open import M` and `import x` are both bare because NEITHER SELECTS; the fact that python
    then requires `x.y` at the use site is the qualification, a different axis.  A first reading
    of this correspondence had `import x` as the violation precisely because `x.y` "looks
    qualified" — but qualification is what makes the use site name its definition site, which is
    the policy, not a breach of it.

    ⚑ SCOPE IS REPORTED, NEVER USED TO EXCUSE.  The operator ruled the ban extends into function
    bodies, and ALSO did not ban `import x` inside one — so placement is orthogonal to form.  A
    function-scoped `from x import y` is a violation; a function-scoped `import x` is compliant
    and remains the cycle-break and the lazy-optional-dependency idiom.  The `scope` column
    exists so that a repair can find the deferred sites, not so they can be discounted.

    ⚑ LOCAL MODULES ONLY BY DEFAULT (`local_only`).  `from typing import Optional` is not this
    repo's namespace to govern, and counting stdlib/third-party would drown the population the
    policy is about — the same scoping the agda ban has, where only `Substrate.*` imports are
    subject.  `local_only=False` reports everything, which is how you check that the local/
    foreign split is itself right rather than assumed.
    """
    files = list(paths or _pycodemod_core.py_files())
    # ⚑ LOCALITY COMES FROM THE CORPUS, NEVER FROM THE SCOPE — and deriving it from `files`
    # produced a FALSE ZERO on the first run. Asked about ONE file, `local` held only that
    # file's own stem, so every import it made read as foreign and the census reported
    # "0 of 0 local import(s)" for a file whose header is a nine-name `from` block. A scoped
    # question must narrow WHICH SITES ARE REPORTED, never what counts as local — otherwise
    # the answer changes with the question, which is the census-keyed-on-one-spelling shape
    # with the spelling supplied by the caller.
    local = ({os.path.splitext(os.path.basename(str(p)))[0] for p in _pycodemod_core.py_files()}
             | {os.path.splitext(os.path.basename(str(p)))[0] for p in files}
             | {os.path.splitext(os.path.basename(str(q)))[0]
                for p in files for q in _sibling_modules(p)})
    # ⚑⚑ A PACKAGE DIRECTORY IS A LOCAL MODULE HEAD, and keying only on FILE STEMS missed an
    # entire import style. `scratch/eliza/` spells its internal imports package-qualified —
    # `from eliza.chain_symbol import ChainSymbol` — whose head is `eliza`, a DIRECTORY, not a
    # `.py` stem. Every one read as foreign, so the census answered "0 of 0 local import(s)"
    # over a package with real internal coupling (measured: 9 of 10 violating in one file).
    #
    # ⚑ AND I MISREAD THAT ZERO TWICE BEFORE MEASURING IT. First as the single-file locality
    # bug recurring at directory scope (wrong — that one is fixed). Then, after opening
    # `sequitur.py` and finding it imports only stdlib, as CORRECT (also wrong — that file
    # happens to have no local imports at all, so it cannot distinguish the two explanations).
    # A file chosen because it was convenient could not settle the question; one chosen
    # because it DOES import siblings did.
    local |= {os.path.basename(os.path.dirname(str(p))) for p in files}
    local |= {os.path.basename(os.path.dirname(str(q)))
              for p in files for q in _sibling_modules(p)}
    out = []
    for p in files:
        try:
            with open(p, encoding="utf-8", errors="replace") as fh:
                tree = ast.parse(fh.read(), filename=str(p))
        except (SyntaxError, OSError):
            continue
        # A node's scope is decided by whether any function/class body encloses it. Walking the
        # tree twice (once for enclosures, once for imports) keeps this independent of ast.walk's
        # order, which is not documented to be depth-first-with-parents.
        enclosed = set()
        for fn in ast.walk(tree):
            if isinstance(fn, (ast.FunctionDef, ast.AsyncFunctionDef)):
                for inner in ast.walk(fn):
                    if isinstance(inner, (ast.Import, ast.ImportFrom)):
                        enclosed.add(id(inner))
        for node in ast.walk(tree):
            scope = "func" if id(node) in enclosed else "module"
            if isinstance(node, ast.Import):
                for a in node.names:
                    head = a.name.split(".")[0]
                    if local_only and head not in local:
                        continue
                    out.append((p, node.lineno, "AS-MOD" if a.asname else "BARE",
                                a.name, [a.asname or a.name], scope))
            elif isinstance(node, ast.ImportFrom):
                mod = node.module or ""
                head = mod.split(".")[0]
                # ⚑ A RELATIVE IMPORT HAS NO MODULE HEAD TO TEST, so `local_only` cannot filter
                # it by name — but `from . import y` is BY CONSTRUCTION local, which is why it
                # is admitted rather than skipped. Skipping would have hidden a violation class
                # behind a filter written for foreign modules.
                if node.level:
                    out.append((p, node.lineno, "RELATIVE", "." * node.level + mod,
                                sorted(a.asname or a.name for a in node.names), scope))
                    continue
                if local_only and head not in local:
                    continue
                if any(a.name == "*" for a in node.names):
                    form = "FROM-STAR"
                elif any(a.asname for a in node.names):
                    form = "FROM-AS"
                else:
                    form = "FROM"
                out.append((p, node.lineno, form, mod,
                            sorted(a.name + (" as " + a.asname if a.asname else "")
                                   for a in node.names), scope))
    return sorted(out, key=lambda r: (str(r[0]), r[1]))


# The forms this repo's import policy admits. Everything else is a violation, and the split is
# DATA so the reporter cannot drift from the docstring above.
ALIAS_COMPLIANT = ("BARE",)


def _declared_deps():
    """Every distribution named in pyproject.toml, base and extras — as IMPORT names.

    ⚑ A DISTRIBUTION NAME IS NOT AN IMPORT NAME, and treating them as one is how a
    declared dependency reads as UNDECLARED: `persist-queue` imports as
    `persistqueue`, `opentelemetry-sdk` as `opentelemetry`.  We ask the installed
    metadata which files a distribution provides rather than guessing a
    transformation -- the same rule as resolving a module by importing it instead
    of assuming its path.
    """
    path = os.path.join(_pycodemod_core.ROOT, "pyproject.toml")
    try:
        import tomllib
        with open(path, "rb") as fh:
            data = tomllib.load(fh)
    except Exception:
        return set()
    proj = data.get("project", {})
    dists = list(proj.get("dependencies", []) or [])
    for extra in (proj.get("optional-dependencies", {}) or {}).values():
        dists.extend(extra or [])
    out = set()
    for d in dists:
        # strip any version/marker specifier: `mypy>=1.0` -> `mypy`
        name = re.split(r"[<>=!~\[; ]", d.strip(), 1)[0]
        if not name:
            continue
        out.add(name.replace("-", "_").lower())
        try:
            import importlib.metadata as _md
            for f in (_md.files(name) or []):
                parts = str(f).split("/")
                if len(parts) > 1 and parts[0] not in ("..", ""):
                    if not parts[0].endswith(".dist-info"):
                        out.add(parts[0].replace(".py", "").lower())
        except Exception:
            pass
    return out


_PARSE_CACHE = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                            ".cst-cache")

# ⚑ THE CACHE KEY MUST NAME ITS DERIVER, NOT ONLY ITS INPUT.  Bump `_SCHEMA` when
# the cached RECORD SHAPE changes (`_cached_defs` yields `(name, line,
# delegating)` — a fourth field is a bump).  The libcst version is READ rather
# than declared, so an upgrade cannot be forgotten: it changes the key by
# construction and every entry misses once, which is the cheap and correct
# outcome.  A cache whose key omits the deriver can only be kept honest by
# remembering to clear it.
_SCHEMA = 1


def _deriver_tag():
    try:
        import libcst as _lc
        v = getattr(_lc, "__version__", None) or ""
    except Exception:
        v = "absent"
    if not v:
        # ⚑ libcst ships no `__version__` on this install (measured: `--available`
        # reports "(no __version__)"), so fall back to the DISTRIBUTION version.
        # A tag that silently resolves to the empty string would defeat the whole
        # point — the key would stop distinguishing derivers and nothing would say so.
        try:
            from importlib import metadata as _md
            v = _md.version("libcst")
        except Exception:
            v = "unknown"
    return "libcst=%s;schema=%d" % (v, _SCHEMA)


_DERIVER = _deriver_tag()


def _ignore_cache():
    """Keep the parse cache out of git — idempotent, appends at most once."""
    rel = os.path.relpath(_PARSE_CACHE, _pycodemod_core.ROOT)
    gi = os.path.join(_pycodemod_core.ROOT, ".gitignore")
    try:
        cur = open(gi, encoding="utf-8").read() if os.path.exists(gi) else ""
        if rel in cur.split():
            return
        with open(gi, "a", encoding="utf-8") as fh:
            if cur and not cur.endswith("\n"):
                fh.write("\n")
            fh.write("%s\n" % rel)
    except OSError:
        pass


def touches(name, path=None):
    """{"files": [...], "symbols": [...]} — what a witness function READS.

    ⚑ PROSE EVIDENCE FINDS ONLY EDGES SOMEONE ALREADY WROTE DOWN (user,
    2026-08-02: *"you can also use ast to identify when one bit of work will
    modify a line of code another bit of work depends on or consumes"*).
    `bibstruct --mentions` measured **0 of 41** for both edges a planning agent
    proposed, and it was right: no entry's PROSE named the relation.  But a
    witness that reads `scripts/worklist_gate.py` genuinely depends on work that
    rewrites `scripts/worklist_gate.py`, whether or not any document says so.
    Those edges are in the CODE, and they are decidable from the AST.

    So there are two edge sources and the worklist had one:
      * prose-warranted  -- `--mentions`: the relation is asserted, undeclared;
      * code-warranted   -- THIS: item A's witness reads what item B's work edits.

    ⚑ A PATH IS A CONSTANT, NOT A GUESS.  `os.path.join(F.ROOT, "scripts",
    "worklist_gate.py")` is a join over string literals, so the file a witness
    reads is recoverable exactly -- no heuristic, no name matching.  A join whose
    parts are not all literal is reported as UNRESOLVED rather than approximated:
    a half-known path silently narrows the edge set, which is the blindness this
    exists to remove.

    Symbols are the string literals the body tests for (`"--set" not in src`),
    which is how every witness here asks "does this tool have this capability" --
    so a rewrite that renames a flag is an edge to every witness naming it."""
    path = path or os.path.join(_pycodemod_core.ROOT, "catalog", "library", "items.py")
    src = open(path, encoding="utf-8").read()
    tree = cst.metadata.MetadataWrapper(cst.parse_module(src))

    class _V(cst.CSTVisitor):
        """⚑ RESOLVE THE BINDING, DO NOT REPORT THE SHAPE (user, 2026-08-02:
        *"ast gives you enough information to trace what read or wrote to that
        variable in that scope; you have that scope information available"*).

        My first cut saw `join(ROOT, "scratch", n)` with `n` a loop variable and
        emitted UNRESOLVED -- which read as "this cannot be known" when it means
        "I did not follow it one hop".  `T26` iterates a LITERAL TUPLE of four
        tool filenames in the same body, so those are four fully-determined
        paths, and calling them unknowable silently shrank the edge set.  Same
        defect as keying by bare name instead of resolving it.

        Three binding forms are followed, all within the function's own scope:
          * `x = "lit"`                     -> one value
          * `for x in ("a", "b")`           -> the element set
          * `import m` / `import m as a`    -> the module's FILE, which is how a
            witness usually reaches a tool (`import bibstruct; B.roundtrip()`)
            and was invisible entirely: `D0-kernel` reads `bibstruct.py` and the
            sweep saw NOTHING, so `0 pairs over 43` measured my extractor, not
            the corpus."""

        def __init__(self):
            self.depth = 0
            self.parts = []
            self.strings = []
            self.binds = {}          # name -> [literal, ...] in this scope
            self.modules = set()

        def visit_FunctionDef(self, node):
            self.depth += node.name.value == name

        def leave_FunctionDef(self, node):
            self.depth -= node.name.value == name

        # --- bindings -------------------------------------------------------
        def visit_Assign(self, node):
            if not self.depth or len(node.targets) != 1:
                return
            tgt = cst.Module(body=[]).code_for_node(node.targets[0].target).strip()
            for lit in self._literals(node.value):
                self.binds.setdefault(tgt, []).append(lit)

        def visit_For(self, node):
            if not self.depth:
                return
            tgt = cst.Module(body=[]).code_for_node(node.target).strip()
            for lit in self._literals(node.iter):
                self.binds.setdefault(tgt, []).append(lit)

        def visit_Import(self, node):
            if self.depth:
                for a in node.names:
                    self.modules.add(
                        cst.Module(body=[]).code_for_node(a.name).strip())

        @staticmethod
        def _literals(node):
            """Every string literal this expression can yield, or []."""
            if isinstance(node, cst.SimpleString):
                v = node.evaluated_value
                return [v] if isinstance(v, str) else []
            if isinstance(node, (cst.Tuple, cst.List, cst.Set)):
                out = []
                for el in node.elements:
                    out.extend(_V._literals(el.value))
                return out
            return []

        # --- uses -----------------------------------------------------------
        def visit_Call(self, node):
            if not self.depth:
                return
            fn = cst.Module(body=[]).code_for_node(node.func)
            if not (fn.endswith("path.join") or fn.endswith("os.path.join")):
                return
            # each argument contributes one or more alternatives
            alts = [[]]
            unresolved = False
            for a in node.args:
                lits = self._literals(a.value)
                if not lits:
                    code = cst.Module(body=[]).code_for_node(a.value).strip()
                    if code.endswith("ROOT"):
                        continue                      # the repo root
                    lits = self.binds.get(code, [])   # ⚑ follow the binding
                    if not lits:
                        unresolved = True
                        continue
                alts = [p + [l] for p in alts for l in lits]
            for p in alts:
                self.parts.append(("/".join(p), unresolved))

        def visit_SimpleString(self, node):
            if self.depth:
                v = node.evaluated_value
                if isinstance(v, str) and v:
                    self.strings.append(v)

    v = _V()
    tree.visit(v)
    # ⚑ AN IMPORTED MODULE IS A FILE THE WITNESS READS.  Resolved against the
    # tool directories rather than assumed: a module that is not ours (stdlib,
    # `paperkit`) contributes no edge and must not be invented as one.
    for mod in sorted(v.modules):
        for d in ("scratch", "scripts"):
            cand = os.path.join(_pycodemod_core.ROOT, d, mod.split(".")[0] + ".py")
            if os.path.exists(cand):
                v.parts.append((f"{d}/{mod.split('.')[0]}.py", False))
                break
    # ⚑ A `sys.path.insert` TARGET IS NOT A FILE THE WITNESS READS, and counting
    # it manufactured the only "shared file" between the two tied items.  Every
    # witness here does `sys.path.insert(0, join(ROOT, "scratch"))` to import the
    # tools, so `scratch` appeared in ALL of them -- a term that is in every set
    # carries no information and would have made every pair look coupled.  A read
    # target is a FILE (it has a suffix); a bare directory is import plumbing.
    files = sorted({p for p, unres in v.parts
                    if p and not unres and os.path.splitext(p)[1]})
    unresolved = sorted({p for p, unres in v.parts if unres})
    # ⚑ A FLAG-SHAPED LITERAL IS THE CAPABILITY BEING PROBED.  Filtering to
    # `--x` / `_name` shapes keeps prose out of the symbol set; a docstring
    # sentence is not a dependency.
    syms = sorted({s for s in v.strings
                   if re.match(r"^(--[a-z][\w-]*|[A-Za-z_]\w+)$", s)
                   and s not in files})
    return {"files": files, "symbols": syms, "unresolved": unresolved}


def paperkit_projects(root=None):
    """[(reldir, cfg, warrants, foreign)] — every paperkit PROJECT in the corpus.

    A paperkit project IS a directory containing `paper.toml`; its `[paper]
    warrants` list names the bibs whose claims it may cite.  A warrant token that
    is a BAZEL LABEL (`//pkg:file`, `@repo//…`) or that resolves OUTSIDE the
    project directory is a FOREIGN bib — a claim-set another project owns — and
    that import is the mechanism by which a computed/derived edge enters the
    claim graph without a bespoke merge file.

    ⚑ THE CORPUS SCOPE COULD BE OPENED AND NOT SURVEYED.  `--in`/`--archive`
    point every query at another tree, and every query answered about its PYTHON;
    asked "how many paperkit projects are in this archive and how do they
    relate", nothing answered, because `py_files` excludes `.toml` and `.bib` by
    construction.  The route left was `find`+`cat`, which is the shell-chaining
    this file forbids.  A project layout is a structural fact about a corpus, so
    it belongs on the tool that owns corpus scope.

    ⚑ FOREIGN IS COMPUTED, NOT DECLARED.  There is no `foreign = true` field:
    a bib is foreign iff its RESOLVED path escapes the project dir.  Deciding it
    by the token's spelling alone would miss `../shared/x.bib` and mis-flag a
    label that happens to resolve locally — the same shape as reading a name
    instead of resolving it.
    """
    import tomllib
    base = root or _pycodemod_core.ROOT
    out = []
    for d, subs, fs in os.walk(base):
        subs[:] = [s for s in subs
                   if s not in _pycodemod_core._GENERATED_DIRS and not s.startswith("bazel-")
                   and s not in ("__pycache__", ".git", ".venv")]
        if "paper.toml" not in fs:
            continue
        try:
            cfg = tomllib.loads(
                open(os.path.join(d, "paper.toml"), "rb").read().decode()
            ).get("paper", {})
        except Exception as e:
            out.append((os.path.relpath(d, base), {"_error": str(e)}, [], []))
            continue
        out.append([os.path.relpath(d, base), cfg,
                    cfg.get("warrants", ["warrants.bib"]), d])
    # ⚑ FOREIGN IS DECIDED BY OWNERSHIP, NOT CONTAINMENT, AND CONTAINMENT GETS THE
    # LIVE CASE BACKWARDS.  paperkit's ROOT project imports `//paper:adequacy_pitch.bib`
    # — a bib the `paper` project owns.  The root project's directory CONTAINS
    # `paper/`, so a "does the path escape my dir" test called it local and
    # reported the repo's one real foreign import as zero: an absence wearing a
    # finding's clothes, in the mode built to find exactly this.  The owner of a
    # bib is the NEAREST enclosing project (longest matching project dir), so a
    # bib is foreign iff that owner is someone else.  This needs the full project
    # set, hence the second pass.
    dirs = sorted((r[3] for r in out), key=len, reverse=True)
    res = []
    for rel, cfg, warrants, d in out:
        foreign = []
        for w in warrants:
            # mirror bib._bibpath: a label is repo-root-relative, else project-relative
            if w.startswith("//") or ":" in w or w.startswith("@"):
                pkg, _, nm = w.split("//", 1)[1].partition(":")
                p = os.path.join(d, pkg, nm) if pkg else os.path.join(d, nm)
            else:
                p = os.path.join(d, w)
            rp = os.path.realpath(p)
            owner = next((o for o in dirs
                          if rp == o or rp.startswith(os.path.realpath(o) + os.sep)),
                         None)
            if owner is None or os.path.realpath(owner) != os.path.realpath(d):
                who = os.path.relpath(owner, base) if owner else "(outside any project)"
                foreign.append((w, os.path.relpath(rp, base), who))
        res.append((rel, cfg, warrants, foreign))
    return sorted(res)


def crossings(paths=None):
    """Containers crossing a FUNCTION BOUNDARY — [(path, fn, line, klass, what)].

    ⚑ THE CLAIM IS UNRESTRICTED (user, 2026-08-05: *"I question whether it's
    correct to pass a container across function boundaries, period"*).  I had
    argued the predicate must be narrower than "returns a container" or it would
    flag the legitimate cases — then failed to produce one.  Every candidate
    dissolved: `_selftest`'s `SIZES`/`PARTS` are MODULE-LEVEL accumulators the
    fold writes, not containers crossing anything; "small, bounded by the
    witness" was the same reasoning that produced every accumulator this session
    (and `A5-as` has 205 parts).  Bounded-by-something-other-than-the-corpus is
    still bounded by something.

    ⚑ SO THERE IS NO EXEMPTION LIST, AND THAT IS DELIBERATE.  An exemption
    declared before the census is a guess about a population nobody has counted;
    this repo has paid for that shape repeatedly (the `PARTITIONED` set the user
    refused, `check_snapshot_guard`'s allow-list).  Rows are CLASSIFIED so a
    reader can judge per row — the same discipline `module_state` states.

    ⚑ AND THE CENSUS TOOL IS IN ITS OWN CENSUS.  `module_state` ends
    `return sorted(out), len(files)`; this function returns rows too.  A census
    that exempted its author would be measuring everything except the thing
    holding the measurement.

    Classes, by what the container's size is a function of:

      corpus  — built by iterating a corpus-shaped source (a file walk, a
                ledger, a tree).  `parse_tree`'s two dicts, 3457 entries each.
                This is the one that costs 217MB.
      derived — accumulated from another container's iteration: an inversion, a
                filter, a group-by.  `_import_dag`'s `rdeps`/`src_to_mod`.
      unfold  — produced by a WORKLIST, a `while`, or recursion: a closure, a
                digit expansion, a path enumeration.  Bounded by nothing the
                signature states, and the canonical `next()` shape — `reach`,
                `quotients`, `to_limbs`, `simple_paths` all live here.
      unattr  — the census CANNOT SEE what bounds this.  A gap in the
                instrument, NOT a licence.

    ⚑ THERE IS NO `local` CLASS, AND NAMING ONE WAS THE DEFECT (user,
    2026-08-05: *"If small returns are taken as acceptable, they become an
    optimisation target, and that's bad"*).  My first cut called the residue
    `local` and I read it as "small returns a paydown need not chase" — a
    THRESHOLD, which reinstates the per-site argument the unrestricted predicate
    exists to end, and which makes SHRINKING a container the sanctioned move
    instead of streaming it.  The Ladder's rule is `R` position-dependent, not
    `R` small.

    ⚑ AND THE CLASS WAS ALSO WRONG ON ITS FACTS.  Reading the 109 rows it held:
    `el-atlas-depsort.reach` is a TRANSITIVE CLOSURE, `euclid-bezout-crt.
    quotients` is a Euclidean digit trace, `simple_paths` enumerates graph
    paths.  None are small; they iterate a WORKLIST or recurse, so no `for` of
    theirs matched the corpus set and they defaulted to the quiet bucket — the
    classifier reporting a fact about its own pattern set as a fact about the
    code.  A census whose quiet class hides closures and digit expansions will
    be read the way I read it."""
    files = list(paths) if paths is not None else _pycodemod_core.py_files()
    # ⚑ CORPUS-SHAPED SOURCES ARE NAMED, because "iterates something" is every
    # loop.  These are the enumeration authorities and the artifact readers —
    # the places a container's size becomes a function of the tree.
    # ⚑ THE CORPUS AUTHORITIES, AND `.items()` IS NOT ONE (caught by a case,
    # 2026-08-05).  I listed `items`/`keys`/`values` here alongside `agda_files`
    # and `walk` — but a dict method says nothing about SIZE: `disk.items()` in
    # `parse_tree` is the corpus, and `src.items()` on a parameter is whatever
    # the caller passed.  The name cannot tell them apart, so listing it flattens
    # exactly the distinction the class exists to draw, and every
    # `for k, v in x.items()` in the tree was reading as `corpus`.
    #
    # ⚑ WHICH MEANS THE LIVE `corpus=165` IS AN OVER-COUNT — recorded here rather
    # than quietly corrected, because the number was reported before the case
    # existed.  These are the ENUMERATION AUTHORITIES: functions whose result is
    # the tree by definition.  Iterating a container is `derived` regardless of
    # how that container is spelled.
    _CORPUS = {"agda_files", "py_files", "walk", "iterdir", "rglob", "glob",
               "readlines", "splitlines", "listdir"}
    _ADD = {"append", "add", "update", "extend", "insert", "setdefault"}
    for p in files:
        try:
            tree = ast.parse(open(p, encoding="utf-8").read(), filename=str(p))
        except (OSError, SyntaxError):
            continue
        for fn in ast.walk(tree):
            if not isinstance(fn, (ast.FunctionDef, ast.AsyncFunctionDef)):
                continue
            # ⚑ A GENERATOR IS NOT A CROSSING — and it is REPORTED, not skipped,
            # so converting one shows as a row moving class rather than as a row
            # vanishing.  A census whose population shrinks on paydown cannot
            # distinguish progress from a predicate that stopped matching.
            if any(isinstance(n, (ast.Yield, ast.YieldFrom))
                   for n in ast.walk(fn)):
                yield (p, fn.name, fn.lineno, "yields", "generator")
                continue
            # locals bound to a container literal/constructor
            built = {}
            for n in ast.walk(fn):
                if isinstance(n, ast.Assign) and len(n.targets) == 1:
                    t, v = n.targets[0], n.value
                    names = ([t.id] if isinstance(t, ast.Name)
                             else [e.id for e in getattr(t, "elts", [])
                                   if isinstance(e, ast.Name)])
                    vals = (list(v.elts) if isinstance(v, ast.Tuple) else [v])
                    for nm, vv in zip(names, vals + [None] * len(names)):
                        if isinstance(vv, (ast.Dict, ast.List, ast.Set)):
                            built[nm] = "dict/list/set"
                        # ⚑ A COMPREHENSION IS THE CORPUS CASE, AND MY FIRST CUT
                        # MISSED IT.  `parse_tree` returns `disk, deps` and only
                        # `disk` was reported: `deps = {m: set() for m in disk}`
                        # is a DictComp, not an Assign-to-a-literal, so `built`
                        # never saw it.  Comprehensions are precisely how a
                        # corpus-shaped container gets built in one expression —
                        # a census blind to them under-counts the class it exists
                        # to find.  Caught by reading the source of a site the
                        # census had already flagged, not by review.
                        elif isinstance(vv, (ast.DictComp, ast.ListComp,
                                             ast.SetComp)):
                            built[nm] = type(vv).__name__
                        elif (isinstance(vv, ast.Call)
                              and isinstance(vv.func, ast.Name)
                              and vv.func.id in ("dict", "set", "list",
                                                 "sorted")):
                            built[nm] = vv.func.id
            if not built:
                continue
            # ⚑ ORDER IS CANONICAL BY CONSTRUCTION, NOT BY A SORT AT THE YIELD
            # (user, 2026-08-05: *"whatever `crossings` is, its order should
            # already be canonical by construction"*).  This was a `set()` with
            # `sorted(crossed)` at the yield — which is the DOWNWARD HALF
            # performed at the point of use: the construction threw the order
            # away and the consumer rebuilt a different one.
            #
            # ⚑ AND THE CANONICAL ORDER WAS ALREADY THERE.  `ast.walk` visits
            # returns in source order and `n.value.elts` is the tuple's own
            # left-to-right order, so `return disk, deps` HAS an order — the one
            # written.  The set destroyed it and `sorted` imposed alphabetical,
            # which is why the row read `deps, disk`.  A dict preserves insertion
            # order and still dedupes across multiple return statements.
            crossed = {}
            for n in ast.walk(fn):
                if not isinstance(n, ast.Return) or n.value is None:
                    continue
                for e in ([n.value] + list(getattr(n.value, "elts", []))):
                    if isinstance(e, ast.Name) and e.id in built:
                        crossed[e.id] = None
                    # `return sorted(out)` / `dict(out)` still hands over a
                    # container — the wrapper is not the escape.
                    elif (isinstance(e, ast.Call) and e.args
                          and isinstance(e.args[0], ast.Name)
                          and e.args[0].id in built):
                        crossed[e.args[0].id] = None
            if not crossed:
                continue
            # ⚑ THE CLASS COMES FROM WHAT PRODUCES THE ELEMENTS, because that is
            # what the size is a function of.  A row that says only "returns a
            # dict" cannot tell 3457 entries from 3.
            #
            # ⚑ YIELD WHERE THE FACT IS FOUND — do not carry a verdict down the
            # tree (user, 2026-08-05).  My first cut set `klass`, kept walking,
            # and yielded at the bottom, which needed `break`s and an
            # `if klass != "unfold"` guard purely to PROTECT A STORED VALUE.
            # That is the accumulator shape one scale down, inside the census
            # built to find it: the complexity was bookkeeping, not logic.
            #
            # ⚑ AND `unattr` BECOMES THE HONEST FALLTHROUGH rather than an
            # initialiser.  Reaching the end without having yielded IS "the
            # census cannot see what bounds this" — the class states itself
            # instead of being the value nobody overwrote.
            # ⚑ NO `sorted()` — the order IS the return statement's.
            what = ", ".join(crossed)

            # ⚑ SPECIFICITY ORDERS THE SCANS, and the ordering is now LOAD-BEARING
            # rather than incidental.  With a stored verdict, `derived` was a soft
            # setting a later `corpus` could overwrite; yielding early means the
            # first match wins, so the most specific producer must be asked first.
            # `reach` walks a worklist with `while stack:` AND a `for` over that
            # stack — a for-first reading files a transitive closure as an
            # ordinary loop.
            for n in ast.walk(fn):
                if isinstance(n, ast.While) or (
                        isinstance(n, ast.Call)
                        and isinstance(n.func, ast.Name)
                        and n.func.id == fn.name):
                    yield (p, fn.name, fn.lineno, "unfold", what)
                    break
            else:
                # ⚑ A GENERATOR, NOT A LIST — and my first cut built `srcs = []`
                # over every loop before testing it: the accumulator reappearing
                # inside the edit that removes one.  `any()` short-circuits, so
                # the whole scan stops at the first corpus hit.
                # ⚑ A WRAPPER HIDES THE SOURCE, AND READING ONLY THE OUTERMOST
                # CALL MADE `corpus` AN UNDER-COUNT (caught 2026-08-05 by reading
                # a row the census had classed).  `ratchet_gates` iterates
                # `sorted(os.listdir(d))` — `listdir` IS a corpus authority — and
                # it classified `derived` because the scan saw `sorted`.  Same
                # for `list(walk())`, `enumerate(py_files())`.  So the scan
                # yields EVERY name on the call chain, not just the head.
                #
                # ⚑ THIS IS THE FOURTH READING OF `corpus` (187, 165, 69, now
                # higher) and every error had one shape: the classifier's PATTERN
                # SET reported as a fact about the code.  Recorded rather than
                # quietly corrected — the earlier figures were published.
                def _srcs():
                    for n in ast.walk(fn):
                        if not isinstance(n, (ast.For, ast.comprehension)):
                            continue
                        it = getattr(n, "iter", None)
                        for sub in ast.walk(it) if it is not None else ():
                            if isinstance(sub, ast.Call):
                                f = sub.func
                                yield (f.attr if isinstance(f, ast.Attribute)
                                       else getattr(f, "id", ""))
                            elif isinstance(sub, ast.Name):
                                yield sub.id
                if any(s in _CORPUS for s in _srcs()):
                    yield (p, fn.name, fn.lineno, "corpus", what)
                elif any(_srcs()):
                    yield (p, fn.name, fn.lineno, "derived", what)
                else:
                    yield (p, fn.name, fn.lineno, "unattr", what)


#: The line count above which a module is REPORTED as over-large.
#:
#: ⚑ A THRESHOLD, NOT A LAW — and stating which it is matters. 1200 is the figure the user
#: cites as commonly applied ("YMMV"), not a measured property of this corpus. It is here so
#: the census has a declared cut rather than a per-reader judgement; it is not a gate, and
#: a file over it is a REPORT, not a failure.
OVERLARGE_LINES = 1200

#: Files that have EXHIBITED the edit-breaks-its-own-region defect → how many times.
#: The threshold for such a file is `OVERLARGE_LINES >> incidents` — HALVED PER INCIDENT.
#:
#: ⚑⚑ BECAUSE DISCIPLINE IS NOT AN INSTRUMENT (user, 2026-08-11: *"Can't rely on discipline.
#: Instead, we cut the split threshold in half for any such affected file."*). The honest
#: diagnosis of these breaks is "I edited a region without reading the enclosing def whole" —
#: which is a resolution, not a measure, and resolutions do not survive the next long session.
#: A per-file threshold that TIGHTENS ON EVIDENCE does: the file that proved hard to edit gets
#: a smaller budget, automatically, whether or not anyone remembers why.
#:
#: ⚑ AND THE GLOBAL CAP DEMONSTRABLY MISSED THESE. `--size` over the five files edited in the
#: session that produced this flagged only `sppf_db.py`; both files actually broken were UNDER
#: 1200. A single corpus-wide number cannot express "this file is harder than its length
#: suggests", which is exactly what an incident record is.
#:
#: ⚑ EACH ENTRY NAMES ITS INCIDENT, so the count is EVIDENCE rather than a magic number. Add a
#: row when a file exhibits the class; never lower a count — this is a ratchet, and paying it
#: down means SPLITTING the file, not editing this table.
INCIDENT_HALVINGS = {
    # ×2: a retirement note placed past a closing `"""` left the module unparseable (the
    # incident that CREATED the 1200 rule); then, hours later, the identical defect in
    # `core_id_for` — prose past the closing quotes, in the file the rule was written for.
    "jea/metalanguage/schema.py": 2,
    # ×1: used `_schema` at :289 while its local `import schema as _schema` sat at :315 —
    # a `NameError` 26 lines out of view, inside one 55-line function.
    "scratch/scope_store.py": 1,
    # ×1: appended an `if __name__` block to a 2823-line file without knowing one existed at
    # :1245; the mid-file block called `sys.exit`, so the new entry point was unreachable and
    # `--selftest` exited 0 in silence. Recorded in `module_size`'s own docstring.
    "scratch/scope_fix.py": 1,
}


def _threshold_for(path, base=OVERLARGE_LINES):
    """The line budget for one file — `base` halved once per recorded incident.

    ⚑ MATCHED ON THE REPO-RELATIVE SUFFIX, not on an absolute path, because the census is run
    from several working directories and an absolute key would silently never match — a
    ratchet that quietly stops ratcheting is worse than none, since the number still prints.
    """
    for rel, n in INCIDENT_HALVINGS.items():
        if path == rel or path.endswith("/" + rel):
            return base >> n, n
    return base, 0


def module_size(paths=None, threshold=OVERLARGE_LINES):
    """[(path, lines, defs, entrypoints, why)] — modules too large to hold in one reading.

    ⚑ THE RULE IS A READING RULE, NOT A STYLE ONE (user, 2026-08-11): *"Any file sufficiently
    large that you're not comfortable reading the whole thing and then writing the whole thing
    back out, modified, is a file that is too large, and such a file requires decomposition."*

    ⚑ AND IT WAS DIAGNOSED FROM A REAL DEFECT, NOT PROPOSED IN THE ABSTRACT. I added an
    `if __name__ == "__main__"` block to the END of `scope_fix.py` (2823 lines) without
    knowing one already existed at :1245 — because I never read the whole file. The mid-file
    block called `sys.exit`, so mine was unreachable: `--selftest` exited 0, silently, and I
    then misdiagnosed the silence as import cost and dispatched two agents on it. The size is
    what made the existing entry point UNFINDABLE; every downstream error followed from that.
    So `entrypoints > 1` is reported as its own signal, not folded into the line count.

    ⚑ THE COUNT IS OF *CODE*, and the distinction is load-bearing in this corpus. These files
    carry dense ⚑ commentary that is the arc's incident log — `pycodemod --roundtrip` exists
    to protect it — so counting comment lines as bulk would flag the most carefully documented
    modules as the worst offenders and push a reader toward deleting the valuable half. `defs`
    is reported alongside because 1200 lines over 40 small functions is a different object
    from 1200 lines over 3.

    ⚑⚑ AND THAT REASONING IS RIGHT ABOUT THE *CAP* AND WRONG ABOUT THE *REPORT* — measured
    2026-08-11 on `sppf_db.py`, which read `1060 code — OK, 140 under its cap` while being
    ~1800 PHYSICAL lines. Both numbers are true and only one was printed, so the file passed
    the metric while being past the point the rule actually names: *"any file sufficiently
    large that you're not comfortable reading the whole thing and then writing the whole
    thing back out."* A reader does not scroll past code lines; they scroll past LINES.
    `module_size_all` therefore carries `physical` alongside `code`, and `--size` prints both.

    ⚑ REPORTED, NEVER CAPPED — the asymmetry is the whole point and collapsing it would undo
    the paragraph above. Only `code` is compared to the threshold, so a well-documented module
    still cannot be flagged for its documentation; `physical` is shown so that "passes on
    code, hard to read" is VISIBLE rather than something a reader has to notice from a line
    number in an editor. The remedy for a large physical count is the same split, chosen for
    the same reason — it is just no longer invisible until someone opens the file.
    """
    rows, nfiles = module_size_all(paths, threshold)
    return [r[:5] for r in rows if r[4]], nfiles


def module_size_all(paths=None, threshold=OVERLARGE_LINES):
    """[(path, code, defs, entrypoints, why, cap, incidents, physical)] for EVERY file —
    violations AND the ones that are fine, with the headroom each has left.

    ⚑ `physical` IS APPENDED AT THE END, NOT INSERTED BESIDE `code`, and the position is the
    point. `module_size` slices `r[:5]` and three selftest cases index these tuples; widening
    in the middle would have shifted `why`/`cap`/`incidents` under every existing reader at
    once — the positional-read defect `schema.Row` exists to retire, reproduced in the census
    that reports it. Appending is the only widening that cannot shift a consumer.

    ⚑ `--size` COULD NOT REPORT A FILE THAT PASSES, AND THAT IS THE QUESTION A SPLIT ASKS.
    `module_size` appends a row only `if why`, so a decomposition that has just cut a module
    from 1,208 to 1,068 gets back an empty list — indistinguishable from "no file was read".
    The next question after every cut is *how far under did it land*, and the fallback was
    reading `--layout`'s trailing total, i.e. running a second mode to recover a number the
    first one computed and threw away.

    ⚑ AND `module_size` IS NOW A FILTER OVER THIS, NOT A SECOND BODY. Two functions counting
    code lines separately is precisely how `agda_files()` became FOUR bodies under one name,
    two of them feeding pre-commit gates. The predicate (`if why`) is the only thing that
    differs, so that is the only thing that is written twice.
    """
    rows = []
    # ⚑ `py_files` TAKES VARARGS, NOT A LIST — passing `paths` positionally hands it `None`
    # and it dies in `os.path.isabs`. The sibling censuses spell this `py_files(*scope) if
    # scope else py_files()`; I wrote a fourth spelling and it was wrong on the first run.
    files = list(paths) if paths else _pycodemod_core.py_files()
    for p in files:
        try:
            src = open(p, encoding="utf-8", errors="replace").read()
        except OSError:
            continue
        try:
            tree = ast.parse(src)
        except SyntaxError:
            continue
        lines = src.splitlines()
        # code lines only — a blank or a full-line comment is not bulk to hold
        code = sum(1 for l in lines
                   if l.strip() and not l.lstrip().startswith("#"))
        defs = sum(1 for n in ast.walk(tree)
                   if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef,
                                     ast.ClassDef)))
        # ⚑ MULTIPLE `if __name__` GUARDS ARE THE SHARPER DEFECT AND ARE REPORTED AT ANY
        # SIZE. A module has ONE entry point; a second is dead code that LOOKS live, and if
        # the first one exits, everything after it is unreachable as a CLI.
        entry = [n.lineno for n in tree.body
                 if isinstance(n, ast.If) and "__main__" in ast.dump(n.test)]
        why = []
        if len(entry) > 1:
            why.append("%d __main__ guards at %s"
                       % (len(entry), ",".join(str(l) for l in entry)))
        # ⚑ THE PER-FILE BUDGET, NOT THE CORPUS ONE. A file with recorded incidents carries a
        # halved threshold; the message SAYS which, because "over cap" reads as a fact about
        # size and this one is a fact about size AND history.
        _cap, _hits = _threshold_for(p, threshold)
        if code > _cap:
            why.append("%d code lines > %d%s"
                       % (code, _cap,
                          " (halved ×%d — recorded edit-breaks-region incidents)" % _hits
                          if _hits else ""))
        rows.append((p, code, defs, len(entry), "; ".join(why), _cap, _hits,
                     len(lines)))
    return rows, len(files)


def module_state(paths=None):
    """[(path, name, line, kind, mutators)] — MODULE-SCOPED MUTABLE STATE.

    ⚑ THE STRUCTURE, NOT THE NAMING CONVENTION (user, 2026-08-04: *"Aren't you
    just looking for module-scoped dicts?"*).  My first cut regex'd bound names
    for `_CACHE|_MEMO`, which asks what something is CALLED — it would have
    missed a cache nobody named one (`_LOG_INDEX`, `_DERIVER`) and matched a
    `_CACHE_DIR` string constant that caches nothing.  A module-level `dict`/
    `set`/`list` that some function MUTATES is the actual shape of process-local
    state, and it is decidable from the tree.

    ⚑ THE MUTATOR LIST IS WHAT MAKES IT A CENSUS AND NOT A GREP.  A module-level
    dict that nothing writes to is a CONSTANT LOOKUP TABLE, not a cache, and
    sweeping it into a "make these Valkey-backed" population would be the
    false-positive-into-a-paydown class this repo has already paid for.  So a
    row carries WHO writes it (subscript-store, `.pop`, `.clear`, `.setdefault`,
    `.append`, `.add`, `.update`), and a row with an empty mutator set is
    reported as `const` rather than silently included.

    ⚑ AND THE POINT OF THE CENSUS IS THAT PROCESS-LOCAL STATE DOES NOT SHARE.
    `agda_lex._MASK_CACHE` measured 58,580 calls / 4,096 live / **10,717
    evicted** — a working set 3.6× its cap, so every eviction is a guaranteed
    recompute, and none of it survives the process.  A shared store makes the
    cap a non-question; the census is how we find the others without listing
    them from memory.

    ⚑ AND "MUTATED" WAS STILL TOO WIDE — 145 rows of which ~134 were NOISE.
    Measured on the first run: `_SNAPPED` (a once-flag, ~25 rows), and every
    `figures/`+`checks/` script whose whole body runs at import, so `bad`,
    `edges`, `stack`, `nodes` are ordinary working variables that merely sit at
    module scope.  Acting on that population is the over-wide-census failure
    this repo keeps paying for.

    A CACHE HAS A STRUCTURAL SIGNATURE AN ACCUMULATOR DOES NOT: **it is READ
    INSIDE A FUNCTION** (a lookup, an `in` test, or a `.get`), which is what
    makes it serve a later call.  An accumulator is written in straight-line
    module code and consumed once, in the same scope.  So the discriminator is
    a read *from within a `FunctionDef`* — not the mutation, which both share.

    Rows are classified, never filtered silently: `cache` (read in a function),
    `accum` (mutated but never read in one), `const` (never mutated).  A caller
    asking for the cache population gets it; a reader can still see what was
    set aside and check the call."""
    files = list(paths) if paths is not None else _pycodemod_core.py_files()
    out = []
    _MUT = {"pop", "clear", "setdefault", "append", "add", "update",
            "extend", "insert", "discard", "remove", "popitem"}
    _READ = {"get", "keys", "values", "items", "setdefault", "pop"}
    for p in files:
        try:
            src = open(p, encoding="utf-8").read()
            tree = ast.parse(src, filename=str(p))
        except (OSError, SyntaxError):
            continue
        # module-level `NAME = {}` / `set()` / `[]`
        cand = {}
        for node in tree.body:
            if not isinstance(node, ast.Assign) or len(node.targets) != 1:
                continue
            tgt = node.targets[0]
            if not isinstance(tgt, ast.Name):
                continue
            v = node.value
            kind = None
            if isinstance(v, ast.Dict):
                kind = "dict"
            elif isinstance(v, ast.Set):
                kind = "set"
            elif isinstance(v, ast.List):
                kind = "list"
            elif (isinstance(v, ast.Call) and isinstance(v.func, ast.Name)
                  and v.func.id in ("dict", "set", "list")):
                kind = v.func.id
            if kind:
                cand[tgt.id] = [node.lineno, kind, set(), False]
        if not cand:
            continue
        for node in ast.walk(tree):
            if isinstance(node, ast.Subscript) and isinstance(node.ctx, ast.Store):
                b = node.value
                if isinstance(b, ast.Name) and b.id in cand:
                    cand[b.id][2].add("[]=")
            elif isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute):
                b = node.func.value
                if (isinstance(b, ast.Name) and b.id in cand
                        and node.func.attr in _MUT):
                    cand[b.id][2].add(node.func.attr)

        # ⚑ THE DISCRIMINATOR: a READ from inside a function body.  Walking each
        # `FunctionDef` separately (rather than the whole tree) is what makes
        # "inside a function" decidable — a module-level read is the accumulator's
        # own consumption and must not count.
        for fn in ast.walk(tree):
            if not isinstance(fn, (ast.FunctionDef, ast.AsyncFunctionDef)):
                continue
            for node in ast.walk(fn):
                nm = None
                if (isinstance(node, ast.Subscript)
                        and isinstance(node.ctx, ast.Load)
                        and isinstance(node.value, ast.Name)):
                    nm = node.value.id
                elif (isinstance(node, ast.Compare)
                      and any(isinstance(o, (ast.In, ast.NotIn))
                              for o in node.ops)):
                    for c in node.comparators:
                        if isinstance(c, ast.Name) and c.id in cand:
                            cand[c.id][3] = True
                elif (isinstance(node, ast.Call)
                      and isinstance(node.func, ast.Attribute)
                      and isinstance(node.func.value, ast.Name)
                      and node.func.attr in _READ):
                    nm = node.func.value.id
                if nm in cand:
                    cand[nm][3] = True

        for nm, (line, kind, muts, read_in_fn) in cand.items():
            if not muts:
                klass = "const"
            elif read_in_fn:
                klass = "cache"
            else:
                klass = "accum"
            out.append((p, nm, line, klass, sorted(muts), kind))
    return sorted(out), len(files)


ROUTE = {
    # ⚑ THE ROUTE IS WHAT TO DO, NOT HOW BAD IT IS (user, 2026-08-05: *"we've
    # reached the point where we can start building out a --diagnose mode"*).
    # The classes were doing two jobs and only one was legitimate: they name
    # WHERE THE SIZE COMES FROM, which is the input to a route.  Read as
    # SEVERITY they became places to file things as acceptable — `local` as
    # "small enough", then `derived` as "second-order".  Both readings were
    # mine, both were wrong, and the verdict was never in the class: `crosses a
    # boundary` is total at 854 with no exemptions.
    "corpus": ("yield the item; hoist the walk to the caller — the enumeration "
               "authority IS the producer"),
    # ⚑ `.items()` IS ALREADY `next()`.  A `for k, v in x.items()` that appends
    # to `out` and returns it takes a lazy pair-stream and un-streams it — worse
    # than the corpus case, because the input was already a stream.  I filed
    # ~100 such rows as "not the problem" one message before being corrected.
    "derived": ("yield the row — the input is already a stream and this "
                "materialises it; the consumer iterates what comes back"),
    # ⚑ NAMED IN THE SUBSTRATE: `Coalg S = S → ℕ × S` with `unfold`/`ana` and
    # `ana-unique` (Substrate.Algebra.R.Trace.Final).  A worklist or a recursion
    # producing digits IS that coalgebra; the repo has the apex and these sites
    # do not reach it.
    "unfold": ("yield each step — this is `Coalg S = S -> elem x S`; the "
               "substrate names it `unfold`/`ana` (Trace.Final)"),
    # ⚑ NOT A LICENCE.  `unattr` means the census cannot see the bound, so the
    # route is to look — honest work, not a verdict.
    "unattr": ("READ IT — the census cannot see what bounds this; classify by "
               "hand, then route"),
    "yields": ("paid — already a generator", ),
}


def _print_diagnose(paths, key=None):
    """The ROUTE per class, with its sites — the route stated ONCE.

    ⚑ MY FIRST CUT PUT THE ROUTE ON EVERY ROW, and the route text is a
    CONTAINER (user, 2026-08-05: *"guess what... the route text is a
    container"*).  Nine `derived` sites each carried a verbatim copy of one
    sentence — the census committing its own finding, in the mode built to
    diagnose it.  The row already carries the CLASS; the sentence is a lookup on
    that class, so copying it per site adds a copy and no information.
    `rowsum` folds a child's SIZE, not the child.

    ⚑ AND IT IS NOT A SECOND TRAVERSAL OF THE POPULATION.  `--crossings` streams
    the rows and this streams the same generator once, bucketing SITE NAMES —
    which is the fold's accumulator, bounded by the class count, not a rebuild
    of the census."""
    files = _pycodemod_core.py_files(*paths) if paths else _pycodemod_core.py_files()
    sites, total = {}, 0
    for p, fn, line, klass, _what in crossings(files):
        total += 1
        if klass == "yields" or (key and klass != key):
            continue
        sites.setdefault(klass, []).append(
            "%s:%d %s" % (os.path.relpath(p, _pycodemod_core.ROOT), line, fn))
    for klass in sorted(sites):
        route = ROUTE.get(klass, "?")
        print("%s (%d) — %s" % (klass, len(sites[klass]),
                                route[0] if isinstance(route, tuple) else route))
        for s in sites[klass]:
            print("    " + s)
    print("diagnose: %d routed of %d crossing(s) in %d file(s)"
          % (sum(len(v) for v in sites.values()), total, len(files)))
    return 0


def _print_crossings(paths, summary=False):
    # ⚑ THE PRINTER FOLDS, IT DOES NOT COLLECT.  Counting rows into a dict of
    # counts is O(classes); building a list of rows to sort would be O(corpus) —
    # the census reproducing its own finding, which happened three times in the
    # edit that motivated this mode.
    by, shown, files = {}, 0, _pycodemod_core.py_files(*paths) if paths else _pycodemod_core.py_files()
    for p, fn, line, klass, what in crossings(files):
        by[klass] = by.get(klass, 0) + 1
        if klass == "yields":
            continue                       # paid: reported in the tally only
        shown += 1
        # ⚑ `--summary` IS A MODE, NOT A `| tail` (hook, correctly refusing).
        # 854 rows over 747 files is a real answer and an unreadable one; asking
        # for the tally by slicing the output puts the judgement in the turn,
        # where the next reader re-derives it differently.
        if not summary:
            print("  %-8s %s:%d  %s(...) -> %s"
                  % (klass, os.path.relpath(p, _pycodemod_core.ROOT), line, fn, what))
    print("  " + ", ".join("%s=%d" % kv for kv in sorted(by.items())))
    # ⚑ `n of m`, and `m` is the FILE SCOPE — not the matched rows.  A census
    # whose denominator comes from its own hits cannot distinguish "nothing
    # crosses" from "nothing was searched" (the `--key` defect, four times today).
    print("crossings: %d container(s) crossing a boundary in %d file(s)"
          % (shown, len(files)))
    return 0
