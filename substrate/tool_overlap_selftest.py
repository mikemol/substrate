#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Mike Mol
"""The cases for `substrate.tool_overlap` — the divergence is the finding, not the collision.

⚑⚑⚑ TWO TOOLS SPELLING A MODE THE SAME WAY IS ONLY DANGEROUS WHEN THEY ANSWER DIFFERENT
QUESTIONS, because that is when the wrong tool returns a PLAUSIBLE ANSWER instead of an error. So
the arms below assert the VERDICT, not the membership: a reader that got the colliding names right
and the agreement wrong would look correct while reporting the opposite of the truth.

⚑⚑ AND THE UNDOCUMENTED LAYER IS STRICTLY WORSE. A flag two tools both accept that no usage line
mentions cannot be checked against anything before it is typed, and it carries no gloss, so no
verdict is offered at all — the absence IS the finding, and inventing an "aligned" for it would be
the mirror defect.

⚑ ENUMERATED, NOT THRESHOLDED. Every cross-tool pair is examined and the denominator is reported,
so a reader sees what was CONSIDERED rather than what survived a cut someone tuned.

⚑ PARITY AGAINST THE ORIGIN WAS MEASURED FIRST — **67 collisions, 5,698 sibling pairs, 0
disagreements**. The first run reported 12, every one my probe comparing ORDERED tuples where the
pair is unordered: both readers use the same diagonal over inputs in different order, so one
yields `(a, b)` where the other yields `(b, a)`. An artefact of the probe, not of either module.
"""

from __future__ import annotations

import sys
import tempfile
from pathlib import Path

from substrate import tool_census, tool_overlap

# Two tools declaring `--rows` about the SAME thing — aligned.
_ROWS_A = (
    '"""a.py --rows <file>   every table row in a markdown document\n"""\n'
    'import sys\nif "--rows" in sys.argv:\n    run()\n'
)
_ROWS_B = (
    '"""b.py --rows <file>   the table rows a markdown document carries\n"""\n'
    'import sys\nif "--rows" in sys.argv:\n    run()\n'
)

# A third declaring `--rows` about something else entirely — divergent.
_ROWS_C = (
    '"""c.py --rows <query>   execute a database query and print results\n"""\n'
    'import sys\nif "--rows" in sys.argv:\n    run()\n'
)

# Two tools accepting the same flag that NEITHER declares.
_UNDOC_A = (
    '"""d.py --shown <x>   the shown mode\n"""\n'
    'import sys\nif "--hidden" in sys.argv:\n    run()\n'
    'if "--shown" in sys.argv:\n    run()\n'
)
_UNDOC_B = (
    '"""e.py --other <x>   the other mode\n"""\n'
    'import sys\nif "--hidden" in sys.argv:\n    run()\n'
    'if "--other" in sys.argv:\n    run()\n'
)

# Two tools whose modes share an argument shape but not a name.
_SHAPE_A = (
    '"""f.py --alpha <name> [paths]   find a name\n"""\n'
    'import sys\nif "--alpha" in sys.argv:\n    run()\n'
)
_SHAPE_B = (
    '"""g.py --beta <name> [paths]   locate a name\n"""\n'
    'import sys\nif "--beta" in sys.argv:\n    run()\n'
)


def _census(files: dict[str, str]) -> tuple[tool_census.Tool, ...]:
    """Build a fixture tree and return its census."""
    with tempfile.TemporaryDirectory() as where:
        root = Path(where)
        for name, body in files.items():
            path = root / name
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(body, encoding="utf-8")
        return tool_census.census(root)


def _collision(files: dict[str, str], mode: str) -> tool_overlap.Collision | None:
    """Return the collision for one mode over a fixture tree."""
    return next((c for c in tool_overlap.collisions(_census(files)) if c.mode == mode), None)


def a_shared_name_is_reported(out: list[str]) -> int:
    """Check two tools declaring one name collide."""
    got = _collision({"scripts/a.py": _ROWS_A, "scripts/b.py": _ROWS_B}, "--rows")
    if got is None:
        out.append("selftest: a shared mode name was not reported as a collision")
        return 1
    if len(got.owners) != len(("a", "b")):
        out.append(f"selftest: the collision names {len(got.owners)} owner(s)")
        return 1
    return 0


def agreeing_tools_are_aligned(out: list[str]) -> int:
    """Check a shared name over a shared question is NOT the finding.

    ⚑ THE COLLISION IS ONLY A HINT. Two tools that mean the same thing by a name are a convergence,
    and reporting them as a hazard would drive a rename that makes the vocabulary worse.
    """
    got = _collision({"scripts/a.py": _ROWS_A, "scripts/b.py": _ROWS_B}, "--rows")
    if got is None or got.divergent:
        out.append(f"selftest: agreeing tools read as {got.verdict if got else None!r}")
        return 1
    if tool_overlap.ALIGNED_WORD not in got.verdict:
        out.append(f"selftest: the verdict reads as {got.verdict!r}")
        return 1
    return 0


def disagreeing_tools_are_divergent(out: list[str]) -> int:
    """Check a shared name over DIFFERENT questions is flagged — THE ITEM.

    ⚑⚑ THIS IS WHEN THE WRONG TOOL RETURNS A PLAUSIBLE ANSWER INSTEAD OF AN ERROR, which is the
    only failure mode a name collision actually has.
    """
    got = _collision({"scripts/a.py": _ROWS_A, "scripts/c.py": _ROWS_C}, "--rows")
    if got is None:
        out.append("selftest: the divergent collision was not reported")
        return 1
    if not got.divergent:
        out.append(f"selftest: divergent tools read as {got.verdict!r}")
        return 1
    if tool_overlap.DIVERGENT not in got.verdict:
        out.append(f"selftest: the verdict reads as {got.verdict!r}")
        return 1
    return 0


def one_disagreeing_owner_makes_the_whole_collision_divergent(out: list[str]) -> int:
    """Check the vocabulary is intersected over ALL owners, not pairwise.

    ⚑ THREE TOOLS WHERE TWO AGREE AND THE THIRD DOES NOT IS DIVERGENT, because a reader reaching
    for the name can land on any of them.
    """
    got = _collision(
        {"scripts/a.py": _ROWS_A, "scripts/b.py": _ROWS_B, "scripts/c.py": _ROWS_C}, "--rows"
    )
    if got is None or not got.divergent:
        out.append(f"selftest: a mixed collision read as {got.verdict if got else None!r}")
        return 1
    return 0


def differing_arguments_are_named(out: list[str]) -> int:
    """Check the signature difference is carried in the verdict."""
    got = _collision({"scripts/a.py": _ROWS_A, "scripts/c.py": _ROWS_C}, "--rows")
    if got is None or tool_overlap.DIFFERENT_ARGS.strip(", ") not in got.verdict:
        out.append(
            f"selftest: differing signatures are not named: {got.verdict if got else None!r}"
        )
        return 1
    return 0


def a_lone_declaration_is_not_a_collision(out: list[str]) -> int:
    """Check one owner is not reported — the negative control."""
    if tool_overlap.collisions(_census({"scripts/a.py": _ROWS_A})):
        out.append("selftest: a single declaration was reported as a collision")
        return 1
    return 0


def an_undocumented_flag_shared_by_two_tools_is_reported(out: list[str]) -> int:
    """Check the layer that is strictly worse — and that it offers no verdict.

    ⚑⚑ AN UNDOCUMENTED FLAG HAS NO GLOSS TO COMPARE, so there is nothing to call aligned or
    divergent. A reader cannot check the spelling against anything before typing it, and the
    absence is the finding.
    """
    got = tool_overlap.undocumented_collisions(
        _census({"scripts/d.py": _UNDOC_A, "scripts/e.py": _UNDOC_B})
    )
    if "--hidden" not in got:
        out.append(f"selftest: the shared undocumented flag read as {got!r}")
        return 1
    if len(got["--hidden"]) != len(("d", "e")):
        out.append(f"selftest: the owners read as {got['--hidden']!r}")
        return 1
    return 0


def a_declared_flag_is_not_an_undocumented_collision(out: list[str]) -> int:
    """Check a documented mode is excluded from the undocumented layer."""
    got = tool_overlap.undocumented_collisions(
        _census({"scripts/a.py": _ROWS_A, "scripts/b.py": _ROWS_B})
    )
    if "--rows" in got:
        out.append("selftest: a declared mode appeared in the undocumented layer")
        return 1
    return 0


def modes_sharing_a_signature_are_a_family(out: list[str]) -> int:
    """Check the tightest signal groups by argument shape."""
    got = tool_overlap.signature_families(
        _census({"scripts/f.py": _SHAPE_A, "scripts/g.py": _SHAPE_B})
    )
    if not any(len(members) >= len(("f", "g")) for members in got.values()):
        out.append(f"selftest: the signature families read as {got!r}")
        return 1
    return 0


def modes_sharing_vocabulary_are_siblings(out: list[str]) -> int:
    """Check the coarsest signal pairs differently-named modes — THE WRONG-TOOL PREDICTOR."""
    got = tool_overlap.siblings(_census({"scripts/a.py": _ROWS_A, "scripts/b.py": _ROWS_B}))
    if not got:
        out.append("selftest: two tools with near-identical glosses were not paired")
        return 1
    if len(got[0].shared) < tool_overlap.ALIGNED:
        out.append(f"selftest: a pair below the threshold was reported: {got[0]!r}")
        return 1
    return 0


def a_tool_is_never_its_own_sibling(out: list[str]) -> int:
    """Check two modes on ONE tool are not paired.

    ⚑ THE QUESTION IS WHY SOMEONE REACHES FOR THE WRONG TOOL, so a pair inside one tool answers
    nothing — and would swamp the report with a tool's own internally-consistent vocabulary.
    """
    both = (
        '"""h.py --alpha <x>   every table row a document carries\n'
        'h.py --beta <x>   the table rows in a document\n"""\n'
        'import sys\nif "--alpha" in sys.argv:\n    run()\n'
        'if "--beta" in sys.argv:\n    run()\n'
    )
    if tool_overlap.siblings(_census({"scripts/h.py": both})):
        out.append("selftest: two modes on one tool were reported as siblings")
        return 1
    return 0


def the_denominator_is_available(out: list[str]) -> int:
    """Check the population a sibling count is drawn from can be reported.

    ⚑ ENUMERATED, NOT THRESHOLDED — which is a claim a reader can only weigh against how many
    pairs were EXAMINED.
    """
    rows = _census({"scripts/a.py": _ROWS_A, "scripts/b.py": _ROWS_B, "scripts/c.py": _ROWS_C})
    if tool_overlap.cross_pairs(rows) < len(tool_overlap.siblings(rows)):
        out.append("selftest: the denominator is smaller than the numerator")
        return 1
    return 0


_ARMS = (
    a_shared_name_is_reported,
    agreeing_tools_are_aligned,
    disagreeing_tools_are_divergent,
    one_disagreeing_owner_makes_the_whole_collision_divergent,
    differing_arguments_are_named,
    a_lone_declaration_is_not_a_collision,
    an_undocumented_flag_shared_by_two_tools_is_reported,
    a_declared_flag_is_not_an_undocumented_collision,
    modes_sharing_a_signature_are_a_family,
    modes_sharing_vocabulary_are_siblings,
    a_tool_is_never_its_own_sibling,
    the_denominator_is_available,
)

_CASE_COUNT = 2 + 2 + 3 + 1 + 1 + 1 + 2 + 1 + 1 + 2 + 1 + 1


def selftest() -> int:
    """Run every arm and return an exit code."""
    out: list[str] = []
    failures = sum(arm(out) for arm in _ARMS)

    if failures:
        sys.stderr.write("\n".join(out) + "\n")
        sys.stderr.write(f"tool-overlap selftest: {failures} failure(s)\n")
        return 1
    sys.stdout.write(f"tool-overlap selftest: {_CASE_COUNT}/{_CASE_COUNT}\n")
    return 0


# ⚑ THE FLAG IS NAMED SO `suite_discovery` SEES THIS SUITE (⟡selftest-discovery).
if __name__ == "__main__":
    sys.exit(selftest() if "--selftest" in sys.argv or len(sys.argv) == 1 else 0)
