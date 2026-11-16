# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Mike Mol
"""The cases for `substrate.build_census_render`: the small pure helpers and the block's frame.

⚑ BYTE-EQUALITY WITH THE ORIGIN'S BLOCK was shown by the drain's differential and is now carried
by the committed skill itself: `build_census_skill.cmd_check` fails when the rendered block drifts
from the committed one. These cases pin what a fixture can: absence, stamp format, the frame.
"""

from __future__ import annotations

import re
import sys
import tempfile
from pathlib import Path

from substrate import build_census_render as render

# One opening and one closing fence; one stamp each for the times and the gate-outcome ledgers.
_FENCES = 2
_STAMPS = 2
_STAMP = re.compile(r"^\d{4}-\d{2}-\d{2} \d{2}:\d{2}$")


def _cases(root: Path, scripts: Path) -> list[tuple[str, bool]]:
    """Return `(label, passed)` for every case, against the tree at `root`."""
    block = render.render_block(root, scripts)
    obs = render.render_observations(root, scripts)
    with tempfile.TemporaryDirectory() as tmp:
        here = Path(tmp)
        (here / "present").write_text("x", encoding="utf-8")
        stamped = render.mtime(here / "present")
        absent = render.mtime(here / "nope")
        found = render.exists(here, "present")
        lost = render.exists(here, "nope")
    return [
        ("a file's stamp is minute-resolution local time", bool(_STAMP.match(stamped))),
        ("an unreadable ledger is stamped `absent`, not a traceback", absent == "absent"),
        ("exists answers for a file under the given root", found and not lost),
        ("the structural block opens with the generated notice", block.startswith("⚑ **GENERATED")),
        ("the structural block is one fenced region", block.count("```") == _FENCES),
        ("the structural block carries no trailing newline", not block.endswith("\n")),
        (
            "the observations block carries both ledger stamps",
            obs.count("ledger last written") == _STAMPS,
        ),
        ("the observations block is fenced and unterminated by a newline", obs.endswith("```")),
    ]


def selftest(root: Path, scripts: Path) -> bool:
    """Run every case, reporting failures by name."""
    cases = _cases(root, scripts)
    ok = sum(1 for _, passed in cases if passed)
    for label, passed in cases:
        if not passed:
            sys.stdout.write(f"  FAIL {label}\n")
    sys.stdout.write(f"build-census-render selftest: {ok}/{len(cases)}\n")
    return ok == len(cases)


def main() -> int:
    """Run the suite against the tree this file sits in; the tree is resolved here, at the entry."""
    root = Path(__file__).resolve().parent.parent
    return 0 if selftest(root, root / "scripts") else 1


# ⚑ THE FLAG IS NAMED SO `suite_discovery` SEES THIS SUITE (⟡selftest-discovery).
if __name__ == "__main__":
    sys.exit(main() if ("--selftest" in sys.argv or len(sys.argv) == 1) else 1)
