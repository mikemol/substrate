#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Mike Mol
"""The cases for `substrate.scratch_refs` — two measured misclassifications, and the differential.

⚑⚑⚑ THE DIFFERENTIAL IS THE ARM A DRAIN OWES. Every fixture arm asserts what I believe the reader
SHOULD say; the differential asserts it says what the ORIGIN says, over the live tree, which is a
different claim and the one a replacement actually owes. `check_scratch_independence --scope
jea/metalanguage` reports SEVEN dependency sites in seven files with ONE hard and FIVE mentions;
this module must reproduce every row, or it is a rewrite wearing a refactor's clothes.

⚑⚑ THE TWO FIXTURE ARMS ARE THE ORIGIN'S OWN RECORDED DEFECTS, pinned so they cannot recur:
  - `reasons.append(f"… scratch/ …")` matched on the call NAME while the string was prose in
    an f-string. `append` under a non-`path` receiver must NOT be a dependency.
  - `ast.walk` reached into an f-string's interpolated `relpath(...)` and credited the whole
    node. A path call NAMED inside a diagnostic must NOT be a dependency.
Both are the plausible-and-wrong shape: the file reads as having a coupling it does not have.

⚑ AND THE NEGATIVE CONTROLS ARE AS LOAD-BEARING AS THE POSITIVE ONES. A reader that returned the
empty set would satisfy every "is NOT a dependency" arm, so each pair carries a case that IS one.
"""

from __future__ import annotations

import sys
import tempfile
from pathlib import Path

from substrate import corpus
from substrate import scratch_refs as sr

# The tree the differential reads, and what the origin reported over it.
_TREE = "jea/metalanguage"
_ORIGIN_HARD = "schema.py"
_ORIGIN_MENTIONS = 5

# ⚑⚑ THE FILES, NOT THE LINES (W39). The bulk `ruff format` pass moved every pinned line, so the
# arm went red over a tree whose dependencies had not changed — a pin on WHERE a site sits
# measures the formatter, not the reader. What the reader owes is WHICH files depend and that
# each site's own source line is the scratch path it claims. `sql_lift.py` is absent because
# its dependency is gone from the tree (read 2026-09-25: no site), not because it was dropped
# from the check.
_ORIGIN_FILES = frozenset(
    {
        "graded_orbit.py",
        "numpy_builders.py",
        "query_registry.py",
        "schema.py",
        "schema_diag.py",
        "sql_census.py",
    }
)

# ⚑⚑⚑ ONE KNOWN CORRECTION, ASSERTED RATHER THAN SILENTLY MATCHED. `store.py:706` is
# `_s2.path.insert(0, _o2.path.join(…, "scratch"))` inside a `try:` — a real guarded dependency,
# the canonical shape this gate exists to find. The origin's `--mentions` lists it as NOT a
# runtime dependency. This reader finds it. A differential that matched the origin here would be
# pinning a MISS, so the disagreement is the assertion, and it is excluded from the "extra" check.
#
# ⚑ THE LINE IS THE CALL'S, NOT THE LITERAL'S. `--mentions` reports 706, where the string sits;
# a dependency site is the line of the CALL that consumes it, and that `insert` opens on 705 —
# the same convention every origin dependency row uses (`sql_lift.py:811` is the insert, not
# the string). A first draft pinned 706 from the mentions listing and was wrong by one.
#
# ⚑ PINNED BY THE CALL'S TEXT, NOT ITS LINE (W39): the format pass moved it 705 → 744, and a line
# pin reads that as the reader breaking. ⚑ AND THE FORMAT PASS SPLIT WHAT THE LINE MEANT: while
# the call was one line, "the insert's line" and "the join's line" were the same number. Formatted,
# the insert opens on 742 and the reader reports 744 — the `path.join` that directly consumes the
# `"scratch"` literal. So the pin is the join, which is what the reader has always reported.
_CORRECTED = {"store.py": "path.join"}


def _line(path: Path, number: int) -> str:
    """Return the 1-based source line `number` of `path`, or an empty string past its end."""
    lines = path.read_text(encoding="utf-8").splitlines()
    return lines[number - 1] if 0 < number <= len(lines) else ""


def the_known_correction_is_found_where_the_origin_missed_it(out: list[str]) -> int:
    """Check the one place this reader deliberately disagrees with the origin, and says so."""
    root = corpus.ROOT / _TREE
    bad = 0
    for name, call in _CORRECTED.items():
        deps = sr.dependency_sites(root / name)
        if len(deps) != 1 or call not in _line(root / name, min(deps, default=0)):
            out.append(f"selftest: the known correction {name} ({call}) read {sorted(deps)}")
            bad += 1
        elif sr.guard_depth(root / name, min(deps)) != sr.GUARDED:
            out.append(f"selftest: {name}'s {call} sits inside a try and should read GUARDED")
            bad += 1
    return bad


# A diagnostic that names a path operation without performing one — the descendant trap.
_DIAGNOSTIC = (
    "import os\n"
    "def report(live, root):\n"
    "    reasons = []\n"
    '    reasons.append(f"{len(live)} live scratch/ reference(s); first at "\n'
    '                   f"{os.path.relpath(live[0][0], root)}")\n'
    "    return reasons\n"
)

# The descendant trap on its own: a PATH-SHAPED call whose scratch string sits two levels
# down — inside a nested call inside an f-string argument. The one-level rule must not see it.
#
# ⚑ SEPARATE FROM `_DIAGNOSTIC` BECAUSE A PLANT SHOWED THEY WERE ONE FIXTURE WEARING TWO NAMES.
# Widening the argument walk to `ast.walk` did NOT redden the diagnostic arm, because
# `reasons.append` is rejected on the RECEIVER before any argument is inspected — that fixture
# never reaches the walk. This one is path-shaped, so the walk is the only thing standing.
_NESTED = (
    "import os\n"
    "def where(root):\n"
    '    return os.path.exists(f"{str(root).replace("x", "scratch")}/x")\n'
)

# A real path dependency: a join, a module-level insert, and an import NAMING scratch.
#
# ⚑ THE IMPORT MUST NAME THE NEEDLE. A first draft used `import rungs` and expected it flagged —
# but an import is a dependency only when its NAME contains `scratch`; `rungs` does not. The
# reader was right and the fixture was wrong, which is the direction a differential catches.
_DEPENDENT = (
    "import os, sys\n"
    'ROOT = os.path.join(os.getcwd(), "scratch")\n'
    'sys.path.insert(0, os.path.join(ROOT, "scratch"))\n'
    "from scratch import rungs\n"
)

# The same insert, guarded inside a try.
_GUARDED = (
    "import os, sys\n"
    "try:\n"
    '    sys.path.insert(0, os.path.join("scratch", "lib"))\n'
    "except OSError:\n"
    "    pass\n"
)

# A docstring naming scratch is prose, not a reference.
_DOCSTRING_ONLY = '"""This tool lives in scratch/ for now."""\nX = 1\n'

# Imports whose NAMES contain the word without naming the package — not dependencies — beside
# three spellings that do name it. ⚑ The ruling behind gate-G396: the first scan of `substrate/`
# read every `scratch_*` module of this very drain as a RUNTIME coupling on `scratch/`.
_IMPORT_NAMES = (
    "from substrate import scratch_module\n"
    "import check_scratch_independence\n"
    "from substrate.scratch_refs import scan_file\n"
    "import scratch\n"
    "import scratch.pycodemod\n"
    "from scratch import rungs\n"
)
_IMPORT_DEPS = {4, 5, 6}


def _plant(text: str) -> Path:
    """Write a fixture module and return its path; the caller's directory owns its lifetime."""
    where = Path(tempfile.mkdtemp(prefix="scratch-refs-"))
    target = where / "fixture.py"
    target.write_text(text, encoding="utf-8")
    return target


def _remove(target: Path) -> None:
    target.unlink(missing_ok=True)
    target.parent.rmdir()


def a_diagnostic_naming_a_path_op_is_a_mention_not_a_dependency(out: list[str]) -> int:
    """Check the descendant trap and the `append` trap together — the origin's recorded defects."""
    target = _plant(_DIAGNOSTIC)
    try:
        deps = sr.dependency_sites(target)
        wide = {hit.lineno for hit in sr.scan_file(target).hits}
    finally:
        _remove(target)
    bad = 0
    if deps:
        out.append(f"selftest: a diagnostic read as a dependency at {sorted(deps)}")
        bad += 1
    if not wide:
        out.append("selftest: the wide scan missed the diagnostic — the mention was dropped")
        bad += 1
    return bad


def a_nested_mention_under_a_path_call_is_not_a_dependency(out: list[str]) -> int:
    """Check the descendant trap ALONE: path-shaped call, scratch two levels down, not flagged."""
    target = _plant(_NESTED)
    try:
        deps = sr.dependency_sites(target)
    finally:
        _remove(target)
    if deps:
        out.append(
            f"selftest: a nested mention under a path call read as a dependency at "
            f"{sorted(deps)} — the argument walk reached past one level"
        )
        return 1
    return 0


def a_real_path_use_is_a_dependency(out: list[str]) -> int:
    """Check the positive control: a join, a path insert and an import all register."""
    target = _plant(_DEPENDENT)
    try:
        deps = sr.dependency_sites(target)
    finally:
        _remove(target)
    want = {2, 3, 4}
    if deps != want:
        out.append(f"selftest: dependency sites read {sorted(deps)}, want {sorted(want)}")
        return 1
    return 0


def a_module_level_insert_is_hard_and_a_guarded_one_is_not(out: list[str]) -> int:
    """Check `guard_depth` distinguishes the two, and never says fine."""
    bad = 0
    hard = _plant(_DEPENDENT)
    try:
        if sr.guard_depth(hard, 3) != sr.HARD:
            out.append("selftest: a module-level insert did not read HARD")
            bad += 1
    finally:
        _remove(hard)
    guarded = _plant(_GUARDED)
    try:
        depth = sr.guard_depth(guarded, 3)
        if depth != sr.GUARDED:
            out.append(f"selftest: an insert inside a try read {depth!r}, want GUARDED")
            bad += 1
    finally:
        _remove(guarded)
    return bad


def an_import_names_the_package_not_the_word(out: list[str]) -> int:
    """Check only a top-level `scratch` segment makes an import a dependency, both directions."""
    target = _plant(_IMPORT_NAMES)
    try:
        deps = sr.dependency_sites(target)
        wide = {hit.lineno for hit in sr.scan_file(target).hits}
    finally:
        _remove(target)
    if deps != _IMPORT_DEPS or wide != _IMPORT_DEPS:
        out.append(
            f"selftest: import lines read deps={sorted(deps)} wide={sorted(wide)}, "
            f"want {sorted(_IMPORT_DEPS)} for both"
        )
        return 1
    return 0


def a_docstring_is_exempt(out: list[str]) -> int:
    """Check prose by position is not a reference."""
    target = _plant(_DOCSTRING_ONLY)
    try:
        wide = sr.scan_file(target).hits
    finally:
        _remove(target)
    if wide:
        out.append(f"selftest: a docstring was read as a reference: {wide!r}")
        return 1
    return 0


def an_unparseable_file_warns_rather_than_reading_zero(out: list[str]) -> int:
    """Check the third outcome survives — a file that cannot be scanned is not a clean one."""
    target = _plant("def broken(:\n")
    try:
        found = sr.scan_file(target)
    finally:
        _remove(target)
    if not found.warns:
        out.append("selftest: an unparseable file read as scanned with no warning")
        return 1
    return 0


def the_differential_matches_the_origin_over_the_live_tree(out: list[str]) -> int:
    """Check this reader reproduces `--scope jea/metalanguage` row for row.

    ⚑ THE ORIGIN'S OWN OUTPUT IS THE ORACLE, quoted from a run on the tree this suite reads. If
    the tree moves the numbers move, and that is the arm going red for a REAL reason — the
    pinned lines are the origin's measurement, not this module's.
    """
    root = corpus.ROOT / _TREE
    if not root.is_dir():
        out.append(f"selftest: {_TREE} is not present — the differential cannot run")
        return 1
    bad = 0
    found: dict[str, frozenset[int]] = {}
    mention_total = 0
    for path in sorted(root.glob("*.py")):
        deps = sr.dependency_sites(path)
        if deps:
            found[path.name] = deps
        mention_total += len(sr.mentions(path))
    for name in sorted(_ORIGIN_FILES):
        sites = found.get(name, frozenset())
        if len(sites) != 1 or not all("scratch" in _line(root / name, n) for n in sites):
            out.append(f"selftest: {name} read {sorted(sites)}, expected ONE site naming scratch")
            bad += 1
    extra = set(found) - _ORIGIN_FILES - set(_CORRECTED)
    if extra:
        out.append(f"selftest: dependencies the origin did not report: {sorted(extra)}")
        bad += 1
    hard_sites = found.get(_ORIGIN_HARD, frozenset())
    if not hard_sites or sr.guard_depth(root / _ORIGIN_HARD, min(hard_sites)) != sr.HARD:
        out.append(f"selftest: {_ORIGIN_HARD} did not read HARD as the origin reports")
        bad += 1
    if mention_total != _ORIGIN_MENTIONS:
        out.append(f"selftest: {mention_total} mention(s), origin says {_ORIGIN_MENTIONS}")
        bad += 1
    return bad


_ARMS = (
    a_diagnostic_naming_a_path_op_is_a_mention_not_a_dependency,
    a_nested_mention_under_a_path_call_is_not_a_dependency,
    a_real_path_use_is_a_dependency,
    a_module_level_insert_is_hard_and_a_guarded_one_is_not,
    an_import_names_the_package_not_the_word,
    a_docstring_is_exempt,
    an_unparseable_file_warns_rather_than_reading_zero,
    the_differential_matches_the_origin_over_the_live_tree,
    the_known_correction_is_found_where_the_origin_missed_it,
)

_CASE_COUNT = 2 + 1 + 1 + 2 + 2 + 1 + 1 + 4 + 2


def selftest() -> int:
    """Run every arm and return an exit code."""
    out: list[str] = []
    failures = sum(arm(out) for arm in _ARMS)

    if failures:
        sys.stderr.write("\n".join(out) + "\n")
        sys.stderr.write(f"scratch-refs selftest: {failures} failure(s)\n")
        return 1
    sys.stdout.write(f"scratch-refs selftest: {_CASE_COUNT}/{_CASE_COUNT}\n")
    return 0


# ⚑ THE FLAG IS NAMED SO `suite_discovery` SEES THIS SUITE (⟡selftest-discovery).
if __name__ == "__main__":
    sys.exit(selftest() if "--selftest" in sys.argv or len(sys.argv) == 1 else 0)
