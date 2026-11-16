#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Mike Mol
"""Pin the three outcomes SEPARATELY, and pin that CLOSED has exactly one path.

⚑⚑⚑ THE ONE-GREEN-PATH PROPERTY IS THE POINT, AND IT IS ASSERTED AS A PROPERTY. `Ⓝ162⁗
⟡probe-the-mode-kind` can only be a GUARD if `CLOSED` means one thing — so the suite drives every
reachable state and asserts that exactly one of them is green. A case that only checked the
DOCUMENTED path would pass against a reader returning CLOSED for everything, which is the
inversion this whole kind exists because of. ⚑ And it asserts the PROPERTY, not today's count of
cases: a reach floor stated as a number expires the moment the reach improves.

⚑⚑ THE DELETED CASE IS THE LOAD-BEARING ONE. The origin's defect was a verdict string reading
*"documented (or no longer dispatched)"* — one green over two opposite states. So *the mode is
GONE* is asserted to be OPEN **and** asserted to be distinguishable from *still dispatches*, by
message. Two rows agreeing on the code and differing in the text are two states, not one.

⚑⚑ AND THE DIFFERENTIAL IS WHAT THE PROMOTION ACTUALLY OWES. The fixtures prove the parsers; only
running BOTH implementations over LIVE modes proves this is a move rather than a rewrite. It lives
in the suite rather than in a turn because a differential in an inline script dies with the turn —
which is this drain's own thesis, and the hook refused exactly that while it was being written.

⚑⚑ THE ORIGIN IS READ THROUGH A `Protocol`, AND THAT IS FORCED. A dynamically loaded module is
`Any`, so every read off it type-checks against nothing: a misspelled attribute passes, and a
differential that agrees with anything is worthless. Naming the one function this suite calls
makes the differential's reach explicit as well as sound.

⚑ THE LENSES ARE INJECTED, NEVER PATCHED. `mode_undocumented` takes its runner, so each case
supplies its own and nothing survives into the next one. A module-level swap would make every
later case depend on the order it ran in — the sequence-dependence that makes a suite pass for
the wrong reason.

⚑ THE ROW READERS ARE CASED AGAINST THEIR OWN RECORDED DEFECTS, not against my reading of them.
The origin substringed a column-aligned block and returned a false zero; `--find`'s `⚑ NOT on:`
line lists other tools by path and defeats a name-only test. Both are fixtures here, because a
parser agreeing with a clean fixture proves nothing about the row that broke it.
"""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from typing import TYPE_CHECKING, Protocol, cast

from substrate import finding_mode
from substrate.finding_kinds import CLOSED, OPEN, UNRUNNABLE

if TYPE_CHECKING:
    from substrate.finding_kinds import Verdict

Case = tuple[str, bool]
Lens = tuple[int | None, str]

ROOT = Path(__file__).resolve().parent.parent
ORIGIN = ROOT / ".claude" / "agents" / "findings.py"

# ⚑ COLUMN-ALIGNED ON PURPOSE. The origin matched `"UNDOCUMENTED  " + mode + " "` and this is the
#   spacing that defeated it — a variable run, not the two spaces the pattern assumed.
DIVERGENCE_ROWS = """\
── scratch/mdstruct.py
  UNDOCUMENTED     --rows        dispatched on argv
  UNDOCUMENTED  --spans   dispatched on argv
── scratch/toolmodes.py
  UNDOCUMENTED   --sync    dispatched on argv
"""

# ⚑ THE `NOT on:` LINE IS THIS FIXTURE'S WHOLE VALUE. A substring test for the tool name matches
#   the NEGATIVE list and reports a mode as declared by the tool explicitly said not to have it.
FIND_DECLARED = """\
  --budget  on scratch/mdstruct.py  [usage]  the per-section byte budget
  ⚑ NOT on: scratch/toolmodes.py, scratch/pycodemod.py
"""

FIND_BARE = """\
  --budget  on scratch/mdstruct.py
"""

FIND_ELSEWHERE = """\
  --budget  on scratch/pycodemod.py  [usage]  a different tool entirely
  ⚑ NOT on: scratch/mdstruct.py
"""

FIND_NONE = """\
  --nosuch is declared by NO tool
"""

# The divergence output for a tool whose --budget IS the undocumented row.
DIVERGENCE_BUDGET = DIVERGENCE_ROWS.replace("--rows", "--budget")

TOOL = "scratch/mdstruct.py"
STEM = "mdstruct.py"


class _Origin(Protocol):
    """The one origin function this differential reads — named so a typo cannot pass."""

    def _mode_undocumented(self, tool: str, mode: str) -> tuple[int, str]:
        """Return the origin's verdict for one tool and mode."""
        ...


def _diverges_cases() -> list[Case]:
    """Return the cases pinning the divergence row reader against its recorded defect."""
    return [
        ("a widely-spaced UNDOCUMENTED row is FOUND",
         finding_mode.diverges(DIVERGENCE_ROWS, STEM, "--rows")),
        ("...and so is a narrowly-spaced one",
         finding_mode.diverges(DIVERGENCE_ROWS, STEM, "--spans")),
        # ⚑ THE BLOCK STRUCTURE CASE. A row under a DIFFERENT tool must not answer for this one,
        #   or every shared flag spelling would report a divergence everywhere.
        ("a row under ANOTHER tool does not answer for this one",
         not finding_mode.diverges(DIVERGENCE_ROWS, STEM, "--sync")),
        ("...and that row IS found under its own tool",
         finding_mode.diverges(DIVERGENCE_ROWS, "toolmodes.py", "--sync")),
        ("a mode in no row is absent",
         not finding_mode.diverges(DIVERGENCE_ROWS, STEM, "--budget")),
    ]


def _declared_cases() -> list[Case]:
    """Return the cases pinning the declaration reader against the negative-list hazard."""
    return [
        ("a declaration by THIS tool resolves to its source",
         finding_mode.declared_by(FIND_DECLARED, STEM, "--budget") == "[usage]"),
        # ⚑⚑ THE NEGATIVE LIST. `mdstruct.py` appears in the `NOT on:` line here, so a name-only
        #    test reports a declaration the row explicitly denies.
        ("a tool named ONLY in the NOT-on line is NOT a declarer",
         finding_mode.declared_by(FIND_ELSEWHERE, STEM, "--budget") is None),
        ("...while the tool that DOES declare it resolves",
         finding_mode.declared_by(FIND_ELSEWHERE, "pycodemod.py", "--budget") is not None),
        ("a row with no source field says so rather than crashing",
         finding_mode.declared_by(FIND_BARE, STEM, "--budget") == finding_mode.UNSTATED),
        ("a mode declared by nobody is None",
         finding_mode.declared_by(FIND_NONE, STEM, "--nosuch") is None),
    ]


def _drive(divergence: Lens, find: Lens) -> Verdict:
    """Run the verdict against two stubbed lenses, injected rather than patched."""
    def _lens(*cmd: str) -> Lens:
        return find if "--find" in cmd else divergence

    return finding_mode.mode_undocumented(TOOL, "--budget", _lens)


def _verdict_cases() -> list[Case]:
    """Return the cases asserting each outcome, and that exactly ONE of them is green."""
    dispatches = _drive((0, DIVERGENCE_BUDGET), (0, FIND_NONE))
    documented = _drive((0, ""), (0, FIND_DECLARED))
    deleted = _drive((0, ""), (0, FIND_NONE))
    no_divergence = _drive((None, "boom"), (0, FIND_DECLARED))
    no_find = _drive((0, ""), (None, "boom"))

    every = [dispatches, documented, deleted, no_divergence, no_find]
    greens = [code for code, _why in every if code == CLOSED]
    return [
        ("a mode still dispatching undocumented is OPEN", dispatches[0] == OPEN),
        ("...saying it has no self-description", "no self-description" in dispatches[1]),
        ("a DECLARED mode is CLOSED", documented[0] == CLOSED),
        ("...naming the source that declares it", "[usage]" in documented[1]),
        # ⚑⚑⚑ THE DISJUNCTION THE ORIGIN COLLAPSED. Same code as `dispatches`, different state,
        #     and the message must distinguish them or the filer inherits the ambiguity.
        ("a GONE mode is OPEN, not closed", deleted[0] == OPEN),
        ("...and says the SUBJECT was deleted, not the finding closed", "GONE" in deleted[1]),
        ("...distinguishably from a mode that still dispatches", deleted[1] != dispatches[1]),
        # ⚑ THE THIRD OUTCOME, BOTH LENSES. A failed lens leaves exactly the gap the second lens
        #   exists to close, so it withholds rather than guessing.
        ("a divergence lens that will not run is UNRUNNABLE", no_divergence[0] == UNRUNNABLE),
        ("a find lens that will not run is UNRUNNABLE", no_find[0] == UNRUNNABLE),
        ("...saying DOCUMENTED cannot be told from DELETED",
         "cannot be distinguished" in no_find[1]),
        # ⚑⚑⚑ THE PROPERTY `Ⓝ162⁗` RESTS ON: exactly one reachable state is green. Asserted over
        #     whatever states this suite drives, so adding a state keeps the claim honest.
        ("exactly ONE driven outcome is CLOSED", len(greens) == 1),
    ]


def _origin() -> _Origin | None:
    """Load the origin witness by path, or return None when it cannot be reached."""
    if not ORIGIN.is_file():
        return None
    spec = importlib.util.spec_from_file_location("_origin_findings_mode", ORIGIN)
    if spec is None or spec.loader is None:
        return None
    mod = importlib.util.module_from_spec(spec)
    try:
        spec.loader.exec_module(mod)
    except Exception:  # noqa: BLE001 — a broken origin is a FINDING here, not a crash
        return None
    return cast("_Origin", mod)


def _differential_cases() -> list[Case]:
    """Compare the promoted witness with the origin's, over LIVE modes.

    ⚑⚑⚑ THE FIXTURES PROVE THE PARSERS AND THIS PROVES THE PROMOTION. A module agreeing with my
    fixtures and disagreeing with the tool it replaces has not been verified — the drain owes
    agreement with the ORIGIN's behaviour, which is a different claim from agreement with my
    reading of its comments.

    ⚑⚑ THE VERDICTS ARE COMPARED, NOT THE WORDING. The origin's DELETED message is the collapsed
    disjunction this module was written to split, so pinning the text would assert the defect.
    What must agree is the CODE each returns for a live mode.

    ⚑ AND AN UNREADABLE ORIGIN IS ITS OWN OUTCOME, never a silent pass — it means the differential
    did not run, which is the same third outcome this module keeps for its own lenses.
    """
    origin = _origin()
    if origin is None:
        return [("⚑ the origin is readable, so the differential can run", False)]
    rows = [
        # A mode documented only as a REDIRECT — the `gate-F55` case this kind was filed over.
        ("scratch/findings.py", "--register"),
        ("scratch/findings.py", "--list"),
        # A live, genuinely declared mode, so the CLOSED path is exercised against the tree.
        ("scratch/mdstruct.py", "--budget"),
    ]
    cases: list[Case] = [("the origin loaded, so this differential means something", True)]
    for tool, mode in rows:
        mine = finding_mode.mode_undocumented(tool, mode)
        theirs = origin._mode_undocumented(tool, mode)  # noqa: SLF001 — the origin's own name
        cases.append((f"{Path(tool).name} {mode} agrees with the origin", mine[0] == theirs[0]))
    return cases


def main() -> int:
    """Run every case and report n/m."""
    cases = (_diverges_cases() + _declared_cases() + _verdict_cases()
             + _differential_cases())
    bad = [label for label, holds in cases if not holds]
    print(f"finding_mode: {len(cases) - len(bad)}/{len(cases)}")  # noqa: T201
    for label in bad:
        print(f"  FAIL {label}")  # noqa: T201
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
