#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Mike Mol
"""The cases for `substrate.suite_reach_lens` — the split-following rule and its edges.

⚑⚑ THE LOAD-BEARING ARM IS THE ONE THAT REFUSES TO CROSS INTO A REAL SUITE. Crossing into a
file that has BOTH a body and a dispatch double-counts its cases: they are already reported
under that file's own label. The measured version of this defect read `run_selftests.py` as
227 against its ~96 own sites, because it imports `rungs`, a suite in its own right.

⚑ AND THE `None` ARM IS THE OTHER POLARITY. An unparseable half must poison the WHOLE reading
rather than contribute a partial count, because a partial count understates the suite and
makes a genuine fewer-RAN regression read as honest deletion.

⚑ THE THREE `None` ARMS ARE SEPARATE ON PURPOSE — an unreadable half, an unparseable suite,
and an absent path reach DIFFERENT branches, and an implementation can get one right while
getting another wrong. Fusing them into one arm is the unsplit-family shape this package
records against itself.
"""

from __future__ import annotations

import sys
import tempfile
from pathlib import Path

from substrate import suite_reach_lens

# How many cases the split-out body fixture registers.
_BODY_CASES = 3

# A dispatching file whose body lives in a sibling it imports at module level.
_DISPATCH = """
import body_half


def _selftest():
    return body_half.run()


if __name__ == "__main__":
    if "--selftest" in sys.argv:
        _selftest()
"""

# The split-out half: a body, and no dispatch of its own.
_BODY = """
def _selftest():
    check(1, 1)
    check(2, 2)
    check(3, 3)
"""

# A file that is a suite in ITS OWN right — body AND dispatch.
_OWN_SUITE = """
def _selftest():
    check(1, 1)
    check(2, 2)


if __name__ == "__main__":
    _selftest()
"""


def _write(root: Path, name: str, src: str) -> str:
    """Write one fixture file and return its path."""
    path = root / name
    path.write_text(src, encoding="utf-8")
    return str(path)


def implementation_half_is_recognised(out: list[str]) -> int:
    """Check a body-without-dispatch reads as an implementation half."""
    bad = 0
    if not suite_reach_lens.is_implementation_half(_BODY):
        out.append("selftest: a body with no dispatch was not read as an implementation half")
        bad += 1
    return bad


def a_real_suite_is_not_an_implementation_half(out: list[str]) -> int:
    """Check a file with BOTH halves is not crossed into.

    ⚑ THIS IS THE DOUBLE-COUNT GUARD. Its cases are reported under its own label.
    """
    bad = 0
    if suite_reach_lens.is_implementation_half(_OWN_SUITE):
        out.append(
            "selftest: a file with its own dispatch was read as an implementation "
            "half — its cases would be counted twice"
        )
        bad += 1
    return bad


def a_file_with_no_body_is_not_a_half(out: list[str]) -> int:
    """Check a file with no `_selftest` body is not crossed into."""
    bad = 0
    if suite_reach_lens.is_implementation_half("x = 1\n"):
        out.append("selftest: a file with no _selftest body was read as an implementation half")
        bad += 1
    return bad


def the_split_body_is_counted(out: list[str]) -> int:
    """Check the count spans the sibling the dispatching file imports.

    ⚑ THE MEASURED DEFECT: counting the dispatching file alone read `pycodemod.py` as 0.
    """
    bad = 0
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        parent = _write(root, "dispatch_half.py", _DISPATCH)
        _write(root, "body_half.py", _BODY)
        got = suite_reach_lens.static_cases(parent, index={"body_half": str(root / "body_half.py")})
        if got != _BODY_CASES:
            out.append(f"selftest: the split body contributed {got!r}, expected {_BODY_CASES}")
            bad += 1
    return bad


def an_unparseable_half_reads_none(out: list[str]) -> int:
    """Check an unparseable half poisons the whole reading rather than under-counting."""
    bad = 0
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        parent = _write(root, "dispatch_bad.py", _DISPATCH)
        _write(root, "body_half.py", "def _selftest(:\n")
        got = suite_reach_lens.static_cases(parent, index={"body_half": str(root / "body_half.py")})
        if got is not None:
            out.append(f"selftest: an unparseable half read {got!r}, expected None")
            bad += 1
    return bad


def an_unparseable_suite_reads_none(out: list[str]) -> int:
    """Check a file that cannot itself be parsed reads None, never 0."""
    bad = 0
    with tempfile.TemporaryDirectory() as tmp:
        path = _write(Path(tmp), "broken_self.py", "def _selftest(:\n")
        got = suite_reach_lens.static_cases(path, index={})
        if got is not None:
            out.append(f"selftest: an unparseable suite read {got!r}, expected None")
            bad += 1
    return bad


def a_missing_file_reads_none(out: list[str]) -> int:
    """Check an absent path reads None — a different branch from unparseable."""
    bad = 0
    with tempfile.TemporaryDirectory() as tmp:
        got = suite_reach_lens.static_cases(str(Path(tmp) / "absent.py"), index={})
        if got is not None:
            out.append(f"selftest: an absent suite read {got!r}, expected None")
            bad += 1
    return bad


def a_self_import_is_not_double_counted(out: list[str]) -> int:
    """Check a file resolving to itself in the index contributes its cases once."""
    bad = 0
    with tempfile.TemporaryDirectory() as tmp:
        path = _write(
            Path(tmp), "selfref.py", "import selfref\n\n\ndef _selftest():\n    check(1, 1)\n"
        )
        got = suite_reach_lens.static_cases(path, index={"selfref": path})
        if got != 1:
            out.append(f"selftest: a self-import read {got!r}, expected 1")
            bad += 1
    return bad


_ARMS = (
    implementation_half_is_recognised,
    a_real_suite_is_not_an_implementation_half,
    a_file_with_no_body_is_not_a_half,
    the_split_body_is_counted,
    an_unparseable_half_reads_none,
    an_unparseable_suite_reads_none,
    a_missing_file_reads_none,
    a_self_import_is_not_double_counted,
)

_CASE_COUNT = len(_ARMS)


def selftest() -> int:
    """Run every arm and return an exit code."""
    out: list[str] = []
    failures = sum(arm(out) for arm in _ARMS)
    if failures:
        sys.stderr.write("\n".join(out) + "\n")
        sys.stderr.write(f"suite-reach-lens selftest: {failures} failure(s)\n")
        return 1
    sys.stdout.write(f"suite-reach-lens selftest: {_CASE_COUNT}/{_CASE_COUNT}\n")
    return 0


# ⚑ THE FLAG IS NAMED SO DISCOVERY SEES THIS SUITE (⟡selftest-discovery).
if __name__ == "__main__":
    sys.exit(selftest() if "--selftest" in sys.argv or len(sys.argv) == 1 else 0)
