#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Mike Mol
"""⟡promote-frontier — which modules can be promoted WITHOUT inheriting a callee's debt.

⚑⚑ THE FRONTIER IS NOT "WHICH FILES ARE CLEAN", AND THAT DISTINCTION IS THE WHOLE
POINT. paperkit MEASURED (2026-08-30) what happens when a file is promoted ahead of
its callees: converting three suites from `sys.path.insert` + bare import to named
imports moved them from 3 own findings to 231, from 0 to 17, and from 0 to 312. The
injection was HIDING the debt, not causing it — under a bare `import grade` a checker
cannot follow the edge at all, so the callee's errors are unreachable and the declarer
reads clean. Name the module and the edge becomes followable; the DECLARER then eats a
number it did not create, and under a per-file gate with no partial credit it cannot
land.

⚑ SO EACH SITE IS GATED ON ITS CALLEE, NOT ON ITSELF, and the migration is a
topological walk from the leaves inward rather than a sweep. Converting a module whose
callee is dirty turns a silent hole into a BLOCKED EDIT — strictly worse than leaving
it, because the injection at least still runs. This mode computes the set for which
that cannot happen: a module is ON THE FRONTIER when it is clean AND every module it
transitively imports is clean.

⚑⚑ AND "HAVE WE FINISHED?" HAS NO ANSWER WITHOUT THIS. Asked that today, the only
figure available was a NUMERATOR — nine files clean of roughly a hundred and ten. A
count of clean files reports progress against the wrong denominator, because the ones
that CAN move next are a much smaller set than the ones that are dirty. The frontier is
the denominator that makes the question answerable.
"""

from __future__ import annotations

import ast
import subprocess
import sys
from pathlib import Path

_ROOT = Path(__file__).absolute().parent.parent
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

try:
    from scripts.check_hook_set import _sibling_names
except ImportError as _e:  # pragma: no cover - adoption-shaped, not reachable in-repo
    sys.stderr.write(f"promote_frontier: cannot import a sibling ({_e}).\n")
    sys.exit(0)

_VENV_PY = _ROOT / ".venv" / "bin" / "python3"
_PYPROJECT = _ROOT / "pyproject.toml"
_SCRIPTS = _ROOT / "scripts"

# ⚑⚑ THE POPULATION SPANS EVERY TREE THE IMPORTS REACH, AND STOPPING AT `scripts/` MADE
# THE RANKING WRONG A THIRD TIME. `set1_census_cores.py` reported as a LEAF at 29 own /
# 0 deps — "safe to convert first" — and is structurally UNCONVERTIBLE: it reaches into
# `jea/metalanguage/jea_agdai`, which is not a declared package, so the module object is
# `Any` and no discipline inside the importer can narrow it. MEASURED 2026-08-30: the
# conversion reached 29 -> 3 and stalled on exactly that edge.
#
# ⚑ A CENSUS THAT STOPS AT A DIRECTORY BOUNDARY REPORTS THE BOUNDARY AS THE SUBJECT'S.
# First `_edges` missed bare imports and every module read as a leaf; then `--rank`
# measured own-findings and the best-HIDDEN files ranked cheapest; now the population
# itself ended at `scripts/`. Same defect, three spellings, each caught only by trying
# to act on the answer.
#
# ⚑⚑ AND A FOURTH SPELLING: `substrate` — THE DESTINATION — WAS MISSING, so the tool tracked
# where modules move FROM and not where they move TO. `--blocker substrate/corpus.py`
# answered *"no module spelled that in the population"*, which is a true statement about the
# roster and reads as a false one about the tree. Every module promoted out of `scratch/`
# became invisible to the tool that measures promotion the moment it succeeded — so the
# frontier could only ever shrink, never show progress landing, and a regression introduced
# in a promoted module would not appear in any closure.
#
# ⚑⚑⚑ AND A FIFTH: `tests` AND `catalog` — MEASURED 2026-09-07 AS gate-F60, WITH THE FOUR
# NOTES ABOVE SITTING DIRECTLY ON TOP OF THE CONSTANT THAT CARRIED IT. `intake_manifest`
# builds its population from the WHOLE corpus and asks this reader a question about four
# trees, so a module in neither tree scored `not-promotable` by ABSENCE FROM A SET — which
# is indistinguishable from a measured verdict. All 16 modules that reader named as
# sole-blocked on `not-promotable` lived here, and ruff and mypy both exit 0 on them: they
# were never dirty, they were never walked.
#
# ⚑⚑ THE RECURRENCE IS THE FINDING, NOT THE MISSING NAME. Five spellings of one defect
# means the repair does not belong in a fifth entry — a roster can only ever be as current
# as its last edit, which is this repo's own recorded rule about `_SKIP_TOP`. What makes
# THIS list defensible where that one was not is that it is an ALLOW-list over a corpus with
# no owner: `file_header.population()` is the only reader that spans the whole tree, and it
# is the population `intake_manifest` already joins against. Until this derives from that
# one authority, every consumer asking a whole-corpus question of a four-tree reader
# inherits the same silent false verdict.
_TREES = ("scripts", "jea", "scratch", "substrate", "tests", "catalog")

# ⚑⚑ WIDENING THE POPULATION WITHOUT THIS PRODUCED 197 KB OF NONSENSE, and the failure
# was total rather than partial: the first cross-tree run walked `scratch/.venv/`
# (a vendored python3.8 virtualenv — networkx, setuptools, the lot) and
# `scratch/.edit-snapshots/` (an edit-history directory holding OLD COPIES of files that
# also exist live). Both appeared in the PROMOTABLE list, so the tool recommended
# "convert next: networkx/algorithms/approximation/clique.py".
#
# ⚑ A SNAPSHOT COPY IS THE WORSE HALF. It shares a basename AND a module stem with the
# live file, so it lands in `by_stem` as a rival import target and inflates every
# closure that reaches that stem — a wrong number that looks like a measurement. An
# unfiltered population does not merely add noise; it corrupts the edges.
_EXCLUDED = frozenset(
    {
        ".venv",
        ".edit-snapshots",
        "__pycache__",
        "node_modules",
        ".git",
        "site-packages",
        ".mypy_cache",
        ".ruff_cache",
    }
)


def _sources() -> dict[str, Path]:
    """Return every `.py` in the covered trees, keyed by REPO-RELATIVE path.

    ⚑ KEYED ON THE PATH, NEVER THE BASENAME. Spanning trees makes collision real —
    two directories may both hold `schema.py` — and a basename key would silently merge
    their findings and their edges into one phantom module. The old single-tree form
    could get away with basenames; this one cannot, and the key change is the reason the
    widening is safe rather than a new source of wrong answers.
    """
    out: dict[str, Path] = {}
    for tree in _TREES:
        base = _ROOT / tree
        if not base.is_dir():
            continue
        for p in sorted(base.rglob("*.py")):
            rel = p.relative_to(_ROOT)
            if not _EXCLUDED.isdisjoint(rel.parts):
                continue
            out[str(rel)] = p
    return out


def _clean_set() -> set[str]:
    """Return the basenames under `scripts/` that ruff reports no finding for.

    ⚑ DERIVED FROM THE CHECKER, NEVER A CURATED LIST. A hand-kept roster of "clean
    modules" is a second authority that drifts the moment anyone edits one, which is
    the shape this repo files most often. The checker is asked, every run.
    """
    return set(_sources()) - set(_counts())


def _edges() -> dict[str, set[str]]:
    """Return each module's DIRECT `scripts.*` imports, as basenames.

    ⚑ QUALIFIED IMPORTS ARE THE ONLY SPELLING HERE AND A BARE-NAME READER SEES NONE.
    `pycodemod --importers pycheck_verdict` reports 0 import sites while
    `pycheck_analyze.py` demonstrably imports it, because that mode matches bare module
    names and these files write `from scripts.pycheck_verdict import …`. A census keyed
    on one spelling reports its own boundary as the subject's — so this reuses
    `check_hook_set._sibling_names`, which reads the AST and handles both spellings.
    """
    out: dict[str, set[str]] = {}
    for rel, path in _sources().items():
        try:
            tree = ast.parse(path.read_text(encoding="utf-8"), filename=path.name)
        except (SyntaxError, OSError, UnicodeDecodeError):
            continue
        # `_sibling_names` yields `scripts.<name>` stems; they live under `scripts/`.
        out[rel] = {f"scripts/{m}.py" for m in _sibling_names(tree)}
    return out


def _bare_edges() -> dict[str, set[str]]:
    """Return each module's imports of a SIBLING BY BARE NAME, as basenames.

    ⚑⚑ THIS IS THE EDGE SET `_edges` STRUCTURALLY CANNOT SEE, AND ITS ABSENCE MADE THE
    WHOLE FRONTIER WRONG. `_edges` reads `from scripts.X import …` — the honest,
    checkable spelling. But 92 of 108 modules still mutate `sys.path` and then import a
    sibling by BARE name (`import ratchet`, `from reuse_catalog import generate`), which
    is not a `scripts.*` import and reads as NO EDGE AT ALL. So every unmigrated module
    looked like a leaf, `--rank` reported "0 blocked", and the cheapest files looked
    convertible.

    ⚑⚑⚑ THEY WERE THE BEST-HIDDEN, NOT THE NEAREST DONE. MEASURED 2026-08-30 on the
    first conversion attempted: `gen_reuse_graph.py` reported EIGHT own findings, and
    naming its callee honestly took it to **752** — `reuse_catalog` (332) plus that
    module's own callees, all previously unreachable. paperkit measured the identical
    shape (3 -> 231, 0 -> 312) and the rule that follows is in `pyproject.toml`: type
    the callee, verify it clean, THEN name it. A ranking keyed on own-findings inverts
    that order, because own-findings are LOW exactly when the injection is hiding most.

    ⚑ SO THE BARE EDGE IS THE ONE THAT MATTERS FOR SCHEDULING. A module's real cost is
    its own debt plus everything its bare imports drag in the moment they become
    honest — which is what `--closure` reports and what `--rank` could not.
    """
    srcs = _sources()
    # stem -> the repo-relative paths that could satisfy a bare `import <stem>`.
    # ⚑ A LIST, NOT A SINGLE PATH: `jea/metalanguage/schema.py` and a future
    # `scratch/schema.py` both answer `import schema`, and which one wins depends on
    # `sys.path` order at RUNTIME — something a static reader cannot decide. Recording
    # every candidate keeps the closure CONSERVATIVE (it may over-count a dependency)
    # rather than silently picking one and under-counting.
    by_stem: dict[str, list[str]] = {}
    for rel, p in srcs.items():
        by_stem.setdefault(p.stem, []).append(rel)

    out: dict[str, set[str]] = {}
    for rel, path in srcs.items():
        try:
            tree = ast.parse(path.read_text(encoding="utf-8"), filename=path.name)
        except (SyntaxError, OSError, UnicodeDecodeError):
            continue
        hit: set[str] = set()
        for node in ast.walk(tree):
            heads: list[str] = []
            if isinstance(node, ast.ImportFrom):
                heads = [(node.module or "").split(".", 1)[0]]
            elif isinstance(node, ast.Import):
                heads = [a.name.split(".", 1)[0] for a in node.names]
            for head in heads:
                hit.update(t for t in by_stem.get(head, []) if t != rel)
        out[rel] = hit
    return out


def _closure(name: str, edges: dict[str, set[str]]) -> set[str]:
    """Return every module `name` transitively imports, excluding itself."""
    seen: set[str] = set()
    frontier = set(edges.get(name, set()))
    while frontier:
        nxt = frontier.pop()
        if nxt in seen or nxt == name:
            continue
        seen.add(nxt)
        frontier |= edges.get(nxt, set())
    return seen


def frontier() -> tuple[list[str], list[tuple[str, list[str]]], list[str]]:
    """Return (promotable, blocked-with-blockers, dirty) over `scripts/`.

    ⚑ THREE STATES, NOT TWO, AND THE MIDDLE ONE IS THE FINDING. A clean module whose
    callee is dirty is NOT promotable and NOT itself a paydown target — it is WAITING,
    and naming what it waits on is what turns a wall into a queue. Collapsing it into
    "not ready" would hide that the blocker is one file away.
    """
    clean = _clean_set()
    edges = _edges()
    promotable: list[str] = []
    blocked: list[tuple[str, list[str]]] = []
    dirty: list[str] = []
    for name in sorted(edges):
        if name not in clean:
            dirty.append(name)
            continue
        blockers = sorted(d for d in _closure(name, edges) if d not in clean)
        if blockers:
            blocked.append((name, blockers))
        else:
            promotable.append(name)
    return promotable, blocked, dirty


def _counts() -> dict[str, int]:
    """Return per-module finding counts under `scripts/`, dirtiest last.

    ⚑ THE COUNT IS THE SCHEDULING INPUT AND NOTHING PRODUCED IT. `--statistics` groups
    by RULE across the whole tree, which answers "what kind of debt" and cannot answer
    "which file moves next". Ranking by hand over 92 modules is judgement in the turn;
    this is the same read, keyed by FILE.
    """
    argv = [
        str(_VENV_PY),
        "-m",
        "ruff",
        "check",
        "--config",
        str(_PYPROJECT),
        "--no-cache",
        "--output-format",
        "concise",
        "--quiet",
        # ⚑ THE SAME EXCLUSIONS THE SOURCE MAP APPLIES. Without them ruff lints the
        # vendored venv and the snapshot directory, so `_counts` reports findings for
        # paths `_sources` refuses — and the two halves of the tool disagree about what
        # the population IS.
        *[f"--exclude={e}" for e in sorted(_EXCLUDED)],
        *[str(_ROOT / t) for t in _TREES],
    ]
    p = subprocess.run(argv, capture_output=True, text=True, check=False)
    known = set(_sources())
    out: dict[str, int] = {}
    for line in p.stdout.splitlines():
        head = line.split(":", 1)[0]
        # ⚑ ruff PRINTS PATHS RELATIVE TO ITS OWN CWD, so the key is normalised against
        # the source map rather than trusted: a path that is not a known source is
        # dropped instead of becoming a phantom module with findings and no edges.
        if head.endswith(".py") and head in known:
            out[head] = out.get(head, 0) + 1
    return out


def _render_closure(prefix: str = "") -> int:
    """Print each dirty module's CLOSURE cost — own debt plus its callees' — ascending.

    ⚑ THE COLUMN THAT DECIDES IS `total`, NOT `own`. `own` is what a converted file
    would still owe if its callees were already clean; `total` is what the converting
    edit actually has to clear, because naming a callee makes its debt reachable and
    the per-file gate has no partial credit. A file with own=8 and total=752 is not a
    cheap file — it is a file standing on 744 findings it currently cannot see.

    ⚑⚑ A MODULE WITH `own == total` IS A GENUINE LEAF and is the only safe entry point.
    Those are the frontier: convert them first, and each conversion shrinks the closure
    of everything above it. That is the topological walk `pyproject.toml` prescribes,
    made computable rather than asserted.
    """
    counts = _counts()
    edges = _bare_edges()
    _promotable, _blocked, dirty = frontier()
    # ⚑ THE CLOSURE SPANS EVERY TREE; THE REPORT ANSWERS ABOUT ONE. Widening the
    # population is what makes a cross-tree edge visible, and it also buried the
    # `scripts/` migration under ~700 `scratch/` modules — 48 KB where the question was
    # "what do I convert next in scripts/". Two different sets AGAIN, the third time in
    # this tool: the GRAPH needs every node, the READER needs one subject.
    if prefix:
        dirty = [d for d in dirty if d.startswith(prefix)]
    rows: list[tuple[int, int, int, str]] = []
    for name in dirty:
        own = counts.get(name, 0)
        deps = _closure(name, edges)
        total = own + sum(counts.get(d, 0) for d in deps)
        rows.append((total, own, len(deps), name))
    rows.sort()
    sys.stdout.write("--   total     own  deps  module  (ascending by CLOSURE cost) --\n")
    for total, own, ndeps, name in rows:
        leaf = "  ← LEAF" if total == own else ""
        sys.stdout.write(f"  {total:7d} {own:7d} {ndeps:5d}  {name}{leaf}\n")
    leaves = sum(1 for t, o, _n, _m in rows if t == o)
    sys.stdout.write(
        f"\npromote-frontier: {len(rows)} dirty · {leaves} LEAF (own == total, "
        f"safe to convert first)\n"
        "  ⚑ own is what the file owes ALONE; total is what a conversion must clear,\n"
        "    because naming a callee makes its debt reachable. Convert LEAVES first.\n"
    )
    return 0


def _render_blocker(target: str) -> int:
    """Print the dirty modules inside one target's closure, dirtiest first.

    ⚑⚑ THIS MODE EXISTS BECAUSE `0 blocked` WAS A FACT ABOUT THE METHOD. `frontier()`
    defines BLOCKED as *one callee away from clean*, and across 779 modules nothing is:
    every dirty gate sits behind a 45-deep chain. So the report that names blockers
    printed zero, and reading that as "nothing is blocked" is reading the instrument's
    threshold as the substrate's shape. The census-green-is-a-fact-about-the-census
    reflex, applied to this tool's own output.

    ⚑ `--closure` ANSWERS "WHAT DOES THIS COST", THIS ANSWERS "WHO DO I FIX FIRST".
    Both read the same graph; the difference is which end you hold. Nine ratchet gates
    measured a ~9,880 closure each, which reads as nine problems — it is one chain,
    shared, and until this mode existed naming it required nine `--closure` calls and a
    comparison performed in the turn.
    """
    counts = _counts()
    edges = _bare_edges()
    # ⚑⚑ MEMBERSHIP IS ASKED OF THE POPULATION, NEVER INFERRED FROM AN EMPTY RESULT.
    # The first cut refused when a target had no dirty callees AND no own findings —
    # which is precisely a CLEAN LEAF, the best possible answer, reported as a spelling
    # error. An unknown name and a module with nothing to report are different facts and
    # only the roster can tell them apart; deriving one from two empty lookups is the
    # report-presence-never-absence defect, committed inside the mode written to fix it.
    promotable, blocked, dirty = frontier()
    known = set(promotable) | set(blocked) | set(dirty)
    if target not in known:
        sys.stdout.write(
            f"promote-frontier: no module spelled {target!r} in the population\n"
            "  ⚑ a fact about the QUERY — keys are repo-relative paths\n"
            "    (`scripts/x.py`), not bare module names.\n"
        )
        return 1
    deps = _closure(target, edges)
    rows = sorted(((counts.get(d, 0), d) for d in deps), reverse=True)
    own = counts.get(target, 0)
    carried = sum(n for n, _d in rows)
    sys.stdout.write(f"-- CLOSURE of {target} — dirtiest callee first --\n")
    for n, name in rows:
        if n:
            sys.stdout.write(f"  {n:6d}  {name}\n")
    clean = sum(1 for n, _d in rows if not n)
    sys.stdout.write(
        f"\npromote-frontier: {own} own · {carried} carried over {len(rows)} callee(s) "
        f"({clean} already clean)\n"
        "  ⚑ the TOP ROW is the highest-value target — paying it down shrinks the\n"
        "    closure of every module that reaches it, not just this one.\n"
    )
    return 0


def _render_rank() -> int:
    """Print the dirty modules by finding count, cheapest first.

    ⚑⚑ CHEAPEST-FIRST IS THE ORDER, AND IT IS A SORT RATHER THAN A JUDGEMENT — the
    same rule the Agda driver states for its own queue ("what order?" is a SORT, not a
    judgement call; do not re-derive it as one). A module near the bottom of this list
    can be clean-roomed in one pass; one near the top is a decomposition arc.

    ⚑ AND THE COUNT IS NOT THE WORK. A file with 40 findings that are all `ANN001` is
    an afternoon of annotations; a file with 12 spread across `C901`, `PLR0915` and
    `BLE001` is a redesign. The count ranks; it does not estimate.
    """
    counts = _counts()
    promotable, _blocked, dirty = frontier()
    ranked = sorted((counts.get(n, 0), n) for n in dirty)
    sys.stdout.write("-- DIRTY, cheapest first (finding count · module) --\n")
    for n, name in ranked:
        sys.stdout.write(f"  {n:6d}  {name}\n")
    sys.stdout.write(
        f"\npromote-frontier: {len(promotable)} clean · {len(dirty)} dirty · "
        f"{sum(counts.values())} finding(s)\n"
    )
    return 0


def _render() -> int:
    """Print the frontier, its blocked ring, and the totals."""
    promotable, blocked, dirty = frontier()
    sys.stdout.write("-- PROMOTABLE (clean, and every transitive callee is clean) --\n")
    for name in promotable:
        sys.stdout.write(f"  {name}\n")
    if blocked:
        sys.stdout.write("\n-- CLEAN BUT BLOCKED (waiting on a dirty callee) --\n")
        for name, blockers in blocked:
            sys.stdout.write(f"  {name}\n")
            for b in blockers:
                sys.stdout.write(f"      needs {b}\n")
    total = len(promotable) + len(blocked) + len(dirty)
    sys.stdout.write(
        f"\npromote-frontier: {len(promotable)} promotable · {len(blocked)} blocked · "
        f"{len(dirty)} dirty · {total} module(s)\n"
    )
    sys.stdout.write(
        "  ⛑ PROMOTABLE is the answer to 'what can move next'. DIRTY is the "
        "paydown backlog.\n  BLOCKED is neither: each is one callee away, so its "
        "blocker is the higher-value target.\n"
    )
    return 0


def _edge_cases() -> list[tuple[str, bool]]:
    """Return `(label, passed)` for what the two edge readers can see."""
    edges = _edges()
    bare = _bare_edges()
    s1 = bare.get("scripts/set1_census_cores.py", set())
    return [
        # ⚑ THE QUALIFIED-IMPORT ARM, which is the whole reason this does not reuse
        # `pycodemod --importers`: that mode reports 0 sites for pycheck_verdict while
        # pycheck_analyze imports it. If this reader ever loses the qualified spelling it
        # silently reports every module as a leaf and calls the whole tree promotable.
        (
            "a `from scripts.X import Y` import is an edge",
            "scripts/pycheck_verdict.py" in edges.get("scripts/pycheck_analyze.py", set()),
        ),
        # A module with no sibling imports is a leaf, not an error.
        (
            "a module importing no sibling reads as a leaf",
            not edges.get("scripts/pycheck_message.py"),
        ),
        # ⚑ THE CLOSURE MUST BE TRANSITIVE. hook_pycheck reaches pycheck_verdict only
        # through pycheck_analyze; a one-hop reader calls it promotable while a callee two
        # hops down is dirty — the exact mis-scheduling this mode exists to prevent.
        (
            "the closure reaches a two-hop callee",
            "scripts/pycheck_verdict.py" in _closure("scripts/hook_pycheck.py", edges),
        ),
        # ⚑⚑ THE BARE-EDGE ARM, WITHOUT WHICH THE WHOLE RANKING INVERTS. `_edges` sees only
        # `from scripts.X import …`; 92 modules import siblings by BARE name under a
        # `sys.path` mutation, and reading zero edges for them made every one look like a
        # leaf. MEASURED: gen_reuse_graph reported 8 own findings and cost 752 on
        # conversion. If this reader ever stops seeing bare sibling imports, `--closure`
        # silently degrades back into `--rank` and reports the best-HIDDEN files as the
        # cheapest.
        (
            "a BARE sibling import is an edge too",
            "scripts/reuse_catalog.py" in bare.get("scripts/gen_reuse_graph.py", set()),
        ),
        # ⚑ AND IT MUST NOT COUNT A MODULE AS ITS OWN CALLEE — a self-edge would make every
        # file report an inflated closure and never reach the leaf state.
        (
            "and no module is recorded as its own callee",
            not any(name in deps for name, deps in bare.items()),
        ),
        # ⚑⚑ THE CROSS-TREE ARM, WHICH IS THE WHOLE POINT OF ⟡closure-cross-tree.
        # `set1_census_cores.py` imports `jea_agdai` from `jea/metalanguage` under a
        # `sys.path` prelude. While the population stopped at `scripts/`, that edge was
        # invisible and the file reported as a LEAF — "safe to convert first" — when it is
        # structurally unconvertible until `jea` is a declared package.
        ("a CROSS-TREE import is an edge", any(d.startswith("jea/") for d in s1)),
        # ⚑ AND THE KEYS ARE REPO-RELATIVE PATHS, NEVER BASENAMES. Spanning trees makes
        # filename collision real; a basename key would merge two files' findings and edges
        # into one phantom module, which is a wrong answer that looks like a tidy one.
        ("every edge key is a repo-relative path", all("/" in k for k in bare)),
    ]


def _population_cases() -> list[tuple[str, bool]]:
    """Return `(label, passed)` for WHICH TREES the reader walks at all.

    ⚑⚑⚑ THE POPULATION IS A SEPARATE SUBJECT FROM THE EDGES, AND MERGING THEM IS WHY THIS
    DEFECT RECURRED FIVE TIMES. Every arm above asks whether an edge inside the walked set
    is visible; none can notice a tree that is never walked, because a module absent from
    `_sources` has no edges to get wrong. The two questions need two readers.

    ⚑⚑ gate-F60: `intake_manifest` scores the WHOLE corpus against this reader's verdict, so
    a tree missing from `_TREES` reads as `not-promotable` by ABSENCE — indistinguishable
    from a measurement. Sixteen clean modules under `tests/` and `catalog/` were reported
    blocked on a property nobody had measured.
    """
    covered = set(_sources())
    promotable, blocked, dirty = frontier()
    known = set(promotable) | set(blocked) | set(dirty)
    return [
        ("the population reaches tests/", any(k.startswith("tests/") for k in covered)),
        ("the population reaches catalog/", any(k.startswith("catalog/") for k in covered)),
        # ⚑⚑ `--blocker` MUST DISTINGUISH "CLEAN" FROM "UNKNOWN", and its first cut did not:
        # a promotable leaf has no dirty callees and no own findings, so inferring membership
        # from two empty lookups reported the best possible answer as a spelling error. Only
        # the roster can tell an unknown name from a module with nothing to report.
        ("and the roster contains this tool itself", "scripts/promote_frontier.py" in known),
    ]


def _selftest() -> int:
    """Run the cases and return an exit code."""
    cases = _edge_cases() + _population_cases()
    failures = [label for label, passed in cases if not passed]
    for label in failures:
        sys.stderr.write(f"  FAIL {label}\n")
    if failures:
        sys.stderr.write(f"promote_frontier selftest: {len(failures)} failure(s)\n")
        return 1
    sys.stdout.write(f"promote_frontier selftest: {len(cases)}/{len(cases)}\n")
    return 0


def main(argv: list[str]) -> int:
    """CLI: render the frontier, or run the cases."""
    if "--selftest" in argv:
        return _selftest()
    if "--closure" in argv:
        i = argv.index("--closure")
        rest = [a for a in argv[i + 1 :] if not a.startswith("-")]
        return _render_closure(rest[0] if rest else "")
    if "--blocker" in argv:
        i = argv.index("--blocker")
        rest = [a for a in argv[i + 1 :] if not a.startswith("-")]
        return _render_blocker(rest[0] if rest else "")
    if "--rank" in argv:
        return _render_rank()
    return _render()


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
