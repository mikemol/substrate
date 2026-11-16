# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Mike Mol
"""The cases for `substrate.build_census_skill`: the entry points, run on a FIXTURE tree.

⚑ THE ORIGIN'S `cmd_*` FUNCTIONS WERE UNTESTABLE ON ANYTHING BUT THE REAL REPO: they resolved the
tree from their own `__file__`. Taking the root as a parameter lets `--gates` and the missing-host
refusal be exercised against a hook this suite writes, without touching the real skill.
"""

from __future__ import annotations

import contextlib
import io
import sys
import tempfile
from pathlib import Path

from substrate import build_census_facts as facts
from substrate import build_census_skill as skill

_HOOK = """\
run "alpha gate" python3 a.py
make -C "$ROOT/agda" -j
# ⟡gqs-precommit-reorder
run "gamma gate" python3 c.py
"""


def _gates_output(root: Path) -> tuple[int, str]:
    """Return `(exit code, stdout)` of `cmd_gates` on `root`."""
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        code = skill.cmd_gates(root)
    return code, buf.getvalue()


def _host_refusal(root: Path) -> str:
    """Return the message `cmd_check` refuses a host-less tree with, or `""`."""
    try:
        skill.cmd_check(root, root / "scripts")
    except skill.BlockError as exc:
        return str(exc)
    return ""


def _cases() -> list[tuple[str, bool]]:
    """Return `(label, passed)` for every case."""
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        hook = root / ".githooks" / "pre-commit"
        hook.parent.mkdir()
        hook.write_text(_HOOK, encoding="utf-8")
        code, text = _gates_output(root)
        refusal = _host_refusal(root)
    lines = text.splitlines()
    return [
        ("`--gates` exits 0", code == 0),
        ("`--gates` opens with the first phase heading", lines[0] == f"== {facts.PHASE_A}"),
        ("`--gates` lists a gate under its phase", "   · alpha gate" in lines),
        ("`--gates` counts both populated phases", "2 declared gate(s) across 2 phase(s)." in text),
        (
            "`--check` on a tree without the skill is a BlockError naming it",
            skill.SKILL_REL in refusal,
        ),
        (
            "the skill is addressed relative to the root, never absolutely",
            skill.SKILL_REL[0] != "/",
        ),
    ]


def selftest() -> bool:
    """Run every case, reporting failures by name."""
    cases = _cases()
    ok = sum(1 for _, passed in cases if passed)
    for label, passed in cases:
        if not passed:
            sys.stdout.write(f"  FAIL {label}\n")
    sys.stdout.write(f"build-census-skill selftest: {ok}/{len(cases)}\n")
    return ok == len(cases)


# ⚑ THE FLAG IS NAMED SO `suite_discovery` SEES THIS SUITE (⟡selftest-discovery).
if __name__ == "__main__":
    sys.exit(0 if ("--selftest" in sys.argv or len(sys.argv) == 1) and selftest() else 1)
