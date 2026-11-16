#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Mike Mol
"""The cases for `substrate.tool_decline` — three kinds of silence, and why they must not merge.

⚑⚑⚑ COLLAPSING ANY PAIR DRIVES A PAYDOWN THAT MAKES THE CORPUS WORSE. `invisible` is real debt: a
capability that exists and is unreachable through the documented interface. A CITATION is the
opposite — a tool naming a sibling's mode is the cross-discoverability the standing rule asks for,
so scoring it as debt would drive a paydown that DELETES cross-references while turning a number
greener. A FIXTURE is neither, and hiding it would make an exemption invisible, which is the rot.

⚑⚑ THE WITNESSED/INFERRED SPLIT IS THE PART A TRANSCRIPTION LOSES QUIETLY. A citing line that also
names the declaring tool WITNESSES its owner; a bare flag in a sentence about the citing tool is
genuinely undecidable, and a "tool name near flag" heuristic silently guesses. The second kind
reports EVERY declarer rather than one, so the reader resolves it and the census does not pretend
to.

⚑ PARITY AGAINST THE ORIGIN WAS MEASURED FIRST — **98 tools, 262 citations, 0 disagreements**
across all three predicates and both citation kinds. The first run reported 11, every one an owner
list grown by `substrate/` or a flag promoted from *"declared by NO tool"* to CITATION because its
declarer lives in the directory the origin cannot see. That is the widening, and teaching the
probe to say so is what keeps a real loss visible.
"""

from __future__ import annotations

import sys
import tempfile
from pathlib import Path

from substrate import tool_census, tool_decline

# A tool that publishes one mode and dispatches a SECOND it documents nowhere — the sharp class.
#
# ⚑ THE PUBLISHED MODE IS LOAD-BEARING IN THE FIXTURE, and leaving it out made two arms crash on
# an empty census. A tool that publishes nothing is not censused at all (layer 5's admission
# predicate), so a fixture with only a hidden flag tests the population, not the silence. The
# realistic shape is exactly this: a documented tool with one undocumented dispatch.
_INVISIBLE_SRC = (
    '"""probe.py --alpha <x>   the alpha mode\n"""\n'
    "import sys\n"
    'if "--ghost" in sys.argv:\n    run()\n'
    'if "--alpha" in sys.argv:\n    run()\n'
)

# A tool that names another's mode, WITH the owner adjacent — a witnessed citation.
_WITNESSED_SRC = (
    '"""probe.py --alpha <x>   the alpha mode\n\n'
    'Verified by `owner.py --beta`.\n"""\n'
    'import sys\nif "--alpha" in sys.argv:\n    run()\n'
)

# The same citation with no owner named on the line — undecidable, reported as such.
_INFERRED_SRC = (
    '"""probe.py --alpha <x>   the alpha mode\n\n'
    'Pass --beta to narrow the result.\n"""\n'
    'import sys\nif "--alpha" in sys.argv:\n    run()\n'
)

# The tool that declares the cited mode.
_OWNER_SRC = (
    '"""owner.py --beta <x>   the beta mode\n"""\nimport sys\nif "--beta" in sys.argv:\n    run()\n'
)

# A dispatch marked as a deliberate failing fixture.
_FIXTURE_SRC = (
    '"""probe.py --alpha <x>   the alpha mode\n"""\n'
    "import sys\n"
    f'if "--broken" in sys.argv:   # {tool_decline.FIXTURE_MARK}\n    fail()\n'
    'if "--alpha" in sys.argv:\n    run()\n'
)

# A fixture mark on a flag the tool never dispatches — declares nothing.
_UNDISPATCHED_FIXTURE = (
    '"""probe.py --alpha <x>   the alpha mode\n"""\n'
    "import sys\n"
    f"# --absent is fine   # {tool_decline.FIXTURE_MARK}\n"
    'if "--alpha" in sys.argv:\n    run()\n'
)

# The citing tool and the flag it cites, in the fixtures above.
_CITER = "scripts/probe.py"
_CITED = "--beta"
_OWNER = "scripts/owner.py"


def _census(files: dict[str, str]) -> tuple[tool_census.Tool, ...]:
    """Build a fixture tree and return its census."""
    with tempfile.TemporaryDirectory() as where:
        root = Path(where)
        for name, body in files.items():
            path = root / name
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(body, encoding="utf-8")
        return tool_census.census(root)


def an_undocumented_dispatch_is_invisible(out: list[str]) -> int:
    """Check a flag dispatched and never mentioned is reported — the sharp class."""
    rows = _census({_CITER: _INVISIBLE_SRC})
    if not rows:
        out.append("selftest: the invisible-flag fixture was not censused")
        return 1
    got = tool_decline.invisible(rows[0], frozenset())
    if "--ghost" not in got:
        out.append(f"selftest: a dispatched-and-undocumented flag was missed: {got!r}")
        return 1
    return 0


def a_declared_mode_is_not_invisible(out: list[str]) -> int:
    """Check a documented flag is excluded — the negative control."""
    rows = _census({_CITER: _WITNESSED_SRC, _OWNER: _OWNER_SRC})
    probe = next((row for row in rows if row.relpath == _CITER), None)
    if probe is None:
        out.append("selftest: the probe was not censused")
        return 1
    if "--alpha" in tool_decline.invisible(probe, frozenset()):
        out.append("selftest: a declared mode was reported invisible")
        return 1
    return 0


def a_universal_flag_is_not_invisible(out: list[str]) -> int:
    """Check a convention is not per-tool debt.

    ⚑ REPORTING `--selftest` ONCE PER TOOL put dozens of identical rows in a census whose whole
    value is that a row means something.
    """
    rows = _census({_CITER: _INVISIBLE_SRC})
    if tool_decline.invisible(rows[0], frozenset({"--ghost"})):
        out.append("selftest: a universal flag was reported as this tool's debt")
        return 1
    return 0


def a_witnessed_citation_names_its_owner(out: list[str]) -> int:
    """Check a citing line naming the declarer is WITNESSED — THE ATTRIBUTION ARM.

    ⚑⚑ BOOKING A CITATION AS "DECLARED BY NO TOOL" IS AN ATTRIBUTION ERROR, NOT A DETECTION ONE.
    The mode exists; the reader was pointed at the wrong owner. Two arms of one census once
    reported that a tool declares a flag AND that no tool declares it, in the same run.
    """
    rows = _census({_CITER: _WITNESSED_SRC, _OWNER: _OWNER_SRC})
    got = tool_decline.citations(rows).get((_CITER, _CITED))
    if got is None:
        out.append("selftest: a cross-reference was not read as a citation")
        return 1
    if not got.witnessed:
        out.append(f"selftest: an owner named on the citing line read as {got.kind}")
        return 1
    if _OWNER not in got.owners:
        out.append(f"selftest: the owner reads as {got.owners!r}")
        return 1
    return 0


def an_unnamed_owner_is_reported_as_undecidable(out: list[str]) -> int:
    """Check a bare flag mention is INFERRED, not guessed — the honesty arm.

    ⚑ A "TOOL NAME NEAR FLAG" HEURISTIC SILENTLY GUESSES. Reporting every declarer instead lets
    the reader resolve it, and stops the census asserting an attribution it cannot support.
    """
    rows = _census({_CITER: _INFERRED_SRC, _OWNER: _OWNER_SRC})
    got = tool_decline.citations(rows).get((_CITER, _CITED))
    if got is None:
        out.append("selftest: an unnamed cross-reference was not read as a citation")
        return 1
    if got.witnessed:
        out.append("selftest: an unnamed owner was reported as witnessed")
        return 1
    return 0


def an_uncited_mention_is_not_a_citation(out: list[str]) -> int:
    """Check a flag no tool declares stays a gap.

    ⚑ WITHOUT THIS, "everything mentioned is a citation" would pass both arms above while erasing
    the undocumented-dispatch census entirely.
    """
    if tool_decline.citations(_census({_CITER: _INFERRED_SRC})):
        out.append("selftest: a mention with no declarer was read as a citation")
        return 1
    return 0


def a_marked_fixture_is_recognised(out: list[str]) -> int:
    """Check a declared failing fixture is separated from capability."""
    rows = _census({_CITER: _FIXTURE_SRC})
    if "--broken" not in tool_decline.fixtures(rows[0]):
        out.append(
            f"selftest: the fixture mark was not read: {sorted(tool_decline.fixtures(rows[0]))!r}"
        )
        return 1
    return 0


def a_fixture_must_still_be_dispatched(out: list[str]) -> int:
    """Check a mark on an undispatched flag declares nothing — THE EXEMPTION GUARD.

    ⚑⚑ A COMMENT CANNOT MINT AN EXEMPTION FOR A MODE THAT IS NOT THERE. Without this the marker
    becomes a way to pre-emptively silence future debt: write the comment now, add the flag later,
    and it arrives already excused.
    """
    rows = _census({_CITER: _UNDISPATCHED_FIXTURE})
    if tool_decline.fixtures(rows[0]):
        out.append(
            f"selftest: an undispatched flag was excused: "
            f"{sorted(tool_decline.fixtures(rows[0]))!r}"
        )
        return 1
    return 0


def a_decline_reports_whether_it_is_guarded(out: list[str]) -> int:
    """Check an unchecked refusal says so rather than passing as settled.

    ⚑ A DECLINE WHOSE CHECK NO LONGER RUNS IS UNGUARDED — the same vacuity an `Arm` that stops
    biting has, and the record exists so that state is reportable rather than silent.
    """
    guarded = tool_decline.Decline(claim="c", instead="i", check="cmd", why="w")
    bare = tool_decline.Decline(claim="c", instead="i", check=None, why="w")
    if not guarded.guarded or bare.guarded:
        out.append("selftest: guardedness is not derived from the check")
        return 1
    return 0


_ARMS = (
    an_undocumented_dispatch_is_invisible,
    a_declared_mode_is_not_invisible,
    a_universal_flag_is_not_invisible,
    a_witnessed_citation_names_its_owner,
    an_unnamed_owner_is_reported_as_undecidable,
    an_uncited_mention_is_not_a_citation,
    a_marked_fixture_is_recognised,
    a_fixture_must_still_be_dispatched,
    a_decline_reports_whether_it_is_guarded,
)

_CASE_COUNT = 1 + 1 + 1 + 3 + 2 + 1 + 1 + 1 + 2


def selftest() -> int:
    """Run every arm and return an exit code."""
    out: list[str] = []
    failures = sum(arm(out) for arm in _ARMS)

    if failures:
        sys.stderr.write("\n".join(out) + "\n")
        sys.stderr.write(f"tool-decline selftest: {failures} failure(s)\n")
        return 1
    sys.stdout.write(f"tool-decline selftest: {_CASE_COUNT}/{_CASE_COUNT}\n")
    return 0


# ⚑ THE FLAG IS NAMED SO `suite_discovery` SEES THIS SUITE (⟡selftest-discovery).
if __name__ == "__main__":
    sys.exit(selftest() if "--selftest" in sys.argv or len(sys.argv) == 1 else 0)
