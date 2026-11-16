#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Mike Mol
"""The cases for `substrate.project_root` — the nearest project wins, and none is an answer.

⚑⚑⚑ THE NESTED CASE IS THE ONE THE DEFECT LIVED IN. A file inside a project inside another
project must be governed by the NEAREST `pyproject.toml`; taking the outermost is how a hook
applied one repo's bar to a second repo's files, demanding an `__init__.py` that would have
destroyed the namespace package being built.

⚑⚑ AND "UNDER NO PROJECT" MUST BE ANSWERABLE. A scratch file outside every checkout is a real
case, and answering it with a default project applies a bar nobody chose — the same defect one
level out from the one this fixes.

⚑ THE INTERPRETER TRAVELS WITH THE CONFIG. A checker run from another project's venv resolves
that project's packages, so a half-migrated module's sibling imports resolve against the wrong
editable install — silently, and toward finding less.
"""

from __future__ import annotations

import sys
import tempfile
from pathlib import Path

from scripts import project_root


def _project(at: Path) -> Path:
    """Create a project root at `at` and return it."""
    at.mkdir(parents=True, exist_ok=True)
    (at / project_root.MARKER).write_text("[project]\n", encoding="utf-8")
    return at


def a_file_finds_its_project(out: list[str]) -> int:
    """Check the containing project is found from a file path."""
    with tempfile.TemporaryDirectory() as d:
        root = _project(Path(d) / "repo")
        src = root / "pkg" / "mod.py"
        src.parent.mkdir(parents=True)
        src.write_text("x = 1\n", encoding="utf-8")
        got = project_root.project_for(src)
    if got != root:
        out.append(f"selftest: the project resolved to {got}, want {root}")
        return 1
    return 0


def the_nearest_project_wins(out: list[str]) -> int:
    """Check a nested project governs its own files, not the outer one.

    ⚑ THE DEFECT'S SHAPE. Taking the outer project is how a foreign file gets a bar it never
    adopted — and the wrong answer looks like a working check, because findings still appear.
    """
    with tempfile.TemporaryDirectory() as d:
        outer = _project(Path(d) / "outer")
        inner = _project(outer / "vendored" / "inner")
        src = inner / "mod.py"
        src.write_text("x = 1\n", encoding="utf-8")
        got = project_root.project_for(src)
    if got != inner:
        out.append(f"selftest: a nested file resolved to {got}, want the inner project")
        return 1
    return 0


def a_file_under_no_project_is_none(out: list[str]) -> int:
    """Check a file outside every project reports none rather than defaulting.

    ⚑ ANSWERING WITH A DEFAULT would apply a bar nobody chose. `None` lets the caller say so.
    """
    with tempfile.TemporaryDirectory() as d:
        src = Path(d) / "loose.py"
        src.write_text("x = 1\n", encoding="utf-8")
        got = project_root.project_for(src)
    if got is not None:
        out.append(f"selftest: a projectless file resolved to {got}")
        return 1
    return 0


def a_directory_resolves_from_itself(out: list[str]) -> int:
    """Check a directory path is searched from itself, not from its parent."""
    with tempfile.TemporaryDirectory() as d:
        root = _project(Path(d) / "repo")
        got = project_root.project_for(root)
    if got != root:
        out.append(f"selftest: a project directory resolved to {got}")
        return 1
    return 0


def the_config_path_is_the_marker(out: list[str]) -> int:
    """Check the config path names the file the checkers are pointed at."""
    with tempfile.TemporaryDirectory() as d:
        root = _project(Path(d) / "repo")
        src = root / "mod.py"
        src.write_text("x = 1\n", encoding="utf-8")
        got = project_root.config_for(src)
    if got != root / project_root.MARKER:
        out.append(f"selftest: the config resolved to {got}")
        return 1
    return 0


def a_project_without_a_venv_reports_none(out: list[str]) -> int:
    """Check a missing interpreter is reported rather than falling back.

    ⚑ FALLING BACK TO WHICHEVER INTERPRETER IS RUNNING resolves the wrong project's packages,
    which is the same wrong-config defect wearing a different name.
    """
    with tempfile.TemporaryDirectory() as d:
        root = _project(Path(d) / "repo")
        got = project_root.venv_python_for(root)
    if got is not None:
        out.append(f"selftest: a venv-less project reported {got}")
        return 1
    return 0


def this_repo_resolves_to_itself(out: list[str]) -> int:
    """Check the resolver agrees with the live tree it will be used on.

    ⚑ THE FIXTURES ABOVE ARE SYNTHETIC; this pins that the same walk answers correctly for a
    real project with a real venv, which is the case the hook actually runs.
    """
    here = Path(__file__).absolute()
    root = project_root.project_for(here)
    bad = 0
    if root is None or not (root / "substrate").is_dir():
        out.append(f"selftest: this module resolved to {root}")
        bad += 1
    if project_root.venv_python_for(here) is None:
        out.append("selftest: this project reported no interpreter")
        bad += 1
    return bad


_ARMS = (
    a_file_finds_its_project,
    the_nearest_project_wins,
    a_file_under_no_project_is_none,
    a_directory_resolves_from_itself,
    the_config_path_is_the_marker,
    a_project_without_a_venv_reports_none,
    this_repo_resolves_to_itself,
)

_CASE_COUNT = 1 + 1 + 1 + 1 + 1 + 1 + 2


def selftest() -> int:
    """Run every arm and return an exit code."""
    out: list[str] = []
    failures = sum(arm(out) for arm in _ARMS)

    if failures:
        sys.stderr.write("\n".join(out) + "\n")
        sys.stderr.write(f"project-root selftest: {failures} failure(s)\n")
        return 1
    sys.stdout.write(f"project-root selftest: {_CASE_COUNT}/{_CASE_COUNT}\n")
    return 0


# ⚑ THE FLAG IS NAMED SO `suite_discovery` SEES THIS SUITE (⟡selftest-discovery).
if __name__ == "__main__":
    sys.exit(selftest() if "--selftest" in sys.argv or len(sys.argv) == 1 else 0)
