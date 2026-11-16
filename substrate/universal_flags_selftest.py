#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Mike Mol
"""The cases for `substrate.universal_flags` — a flag resolved at the authority is not absent.

⚑⚑⚑ THE AUTHORITY-ROUTE CASE IS THE ITEM. The origin's first predicate searched each gate for the
flag STRING and reported 10 of 11 as debt while every one was compliant: the flag is admitted by
`check_argv` on the caller's behalf, precisely so ten call sites do NOT each forward it. A gate
that never mentions `--dry-run` and routes through the authority ACCEPTS it, and the arms below
pin that reading.

⚑⚑ AND THE SELF-DECLARING ROUTE MUST ALSO COUNT. A gate naming the flag itself answers for that
flag without the authority — requiring both routes would report a self-sufficient gate as debt,
requiring neither would report the whole population clean. Two accepting shapes, one verdict.

⚑ THE FIXTURES ARE SOURCE STRINGS. A case reading the live gates measures today's tree — 6 of 23
lack acceptance right now — and would go red the moment one is repaired, reporting correct work
as a defect.
"""

from __future__ import annotations

import sys
import tempfile
from pathlib import Path

from substrate import flag_routing, universal_flags
from substrate.ratchet_flags import UNIVERSAL_FLAGS

# One universal flag, taken from the authority rather than typed.
_FLAG = min(UNIVERSAL_FLAGS)

# ⚑ THE COMPLIANT SHAPE THE ORIGIN MISREAD: no flag string anywhere, routed through the authority.
_ROUTED = '''"""A gate that routes its flags through the authority."""
from substrate.ratchet_flags import check_argv


def main() -> int:
    """Refuse an unknown flag."""
    check_argv(sys.argv)
    return 0
'''

# The other accepting shape: the gate names the flag itself.
_DECLARES = f'''"""A gate declaring the universal flag itself."""


def main() -> int:
    """Preview the write when asked."""
    if "{_FLAG}" in sys.argv:
        return 0
    return 0
'''

# The defect: neither route.
_NEITHER = '''"""A gate accepting nothing."""


def main() -> int:
    """Do the work."""
    return 0
'''

# ⚑ THE SILENT-TYPO SHAPE: it parses one flag by hand and takes a misspelling silently.
_HANDROLLED = '''"""A gate parsing its own flags."""


def main() -> int:
    """Run quietly when asked."""
    if "--quiet" in sys.argv:
        return 0
    return 0
'''


def _acceptance(where: str, text: str) -> universal_flags.Acceptance | None:
    """Write a fixture gate and read its acceptance back."""
    path = Path(where) / "check_fixture.py"
    path.write_text(text, encoding="utf-8")
    return universal_flags.acceptance(path, "check_fixture.py")


def routing_through_the_authority_accepts(out: list[str]) -> int:
    """Check a gate naming no flag but calling the authority ACCEPTS — THE WHOLE ITEM.

    ⚑⚑⚑ THIS IS THE ROW THE ORIGIN CALLED DEBT. Ten of eleven gates had exactly this shape, and
    every one previewed correctly when run — the figure was measuring mentions.
    """
    with tempfile.TemporaryDirectory() as where:
        got = _acceptance(where, _ROUTED)
    if got is None or not got.accepts:
        out.append(f"selftest: a routed gate read as {got!r}")
        return 1
    if got.declared:
        out.append(f"selftest: a routed gate was read as declaring: {got.declared!r}")
        return 1
    return 0


def declaring_the_flag_accepts(out: list[str]) -> int:
    """Check a gate naming the flag itself accepts it.

    ⚑ THE SECOND ROUTE. Requiring the authority as well would report a self-sufficient gate as
    debt — the mirror of the origin's error, in the other direction.
    """
    with tempfile.TemporaryDirectory() as where:
        got = _acceptance(where, _DECLARES)
    if got is None or not got.accepts:
        out.append(f"selftest: a declaring gate read as {got!r}")
        return 1
    if got.declared != (_FLAG,):
        out.append(f"selftest: the declared flags read as {got.declared!r}")
        return 1
    return 0


def neither_route_is_debt(out: list[str]) -> int:
    """Check a gate accepting by neither route is reported — the POSITIVE CONTROL.

    ⚑⚑ WITHOUT THIS, A READER CALLING EVERY GATE COMPLIANT passes both cases above and reports the
    population clean forever. The three arms together say the verdict discriminates.
    """
    with tempfile.TemporaryDirectory() as where:
        got = _acceptance(where, _NEITHER)
    if got is None or got.accepts:
        out.append(f"selftest: a non-accepting gate read as {got!r}")
        return 1
    return 0


def a_handrolled_flag_is_not_acceptance(out: list[str]) -> int:
    """Check parsing an unrelated flag by hand does not count.

    ⚑⚑ THE SILENT-TYPO RESIDUE. A gate testing `"--quiet" in sys.argv` takes `--queit` silently —
    it handles a flag without ACCEPTING the universal ones, and a reader counting any flag-shaped
    literal would call it compliant.
    """
    with tempfile.TemporaryDirectory() as where:
        got = _acceptance(where, _HANDROLLED)
    if got is None or got.accepts:
        out.append(f"selftest: a hand-rolled flag read as acceptance: {got!r}")
        return 1
    return 0


def a_routed_gate_reports_its_route(out: list[str]) -> int:
    """Check the two accepting shapes stay distinguishable.

    ⚑ ONE BOOLEAN WOULD LOSE WHICH ROUTE, and the repair differs: a routed gate needs nothing, a
    self-declaring one needs the authority to gain the NEXT universal flag automatically.
    """
    with tempfile.TemporaryDirectory() as where:
        routed = _acceptance(where, _ROUTED)
        declaring = _acceptance(where, _DECLARES)
    if routed is None or declaring is None:
        out.append("selftest: a fixture failed to parse")
        return 1
    if not routed.routes or declaring.routes:
        out.append(f"selftest: the routes read as {routed.routes!r}, {declaring.routes!r}")
        return 1
    return 0


def the_flag_set_is_read_from_the_authority(out: list[str]) -> int:
    """Check the module measures against the declared universal flags.

    ⚑ A LOCAL COPY GOES STALE IN THE DIRECTION that reports a NEW universal flag as debt across
    every gate at once — a false census produced by the file that defines correctness.
    """
    if not UNIVERSAL_FLAGS:
        out.append("selftest: the authority declares no universal flag")
        return 1
    with tempfile.TemporaryDirectory() as where:
        got = _acceptance(where, _DECLARES)
    if got is None or not set(got.declared) <= UNIVERSAL_FLAGS:
        out.append(f"selftest: a declared flag outside the authority: {got!r}")
        return 1
    return 0


def an_unparseable_gate_yields_nothing(out: list[str]) -> int:
    """Check a syntax error is skipped rather than raising."""
    with tempfile.TemporaryDirectory() as where:
        got = _acceptance(where, "def main(:\n")
    if got is not None:
        out.append(f"selftest: an unparseable gate yielded {got!r}")
        return 1
    return 0


def an_absent_gate_yields_nothing(out: list[str]) -> int:
    """Check a missing file is skipped rather than raising."""
    with tempfile.TemporaryDirectory() as where:
        got = universal_flags.acceptance(Path(where) / "gone.py", "gone.py")
    if got is not None:
        out.append(f"selftest: an absent gate yielded {got!r}")
        return 1
    return 0


def lacking_selects_only_the_non_accepting(out: list[str]) -> int:
    """Check the finding set holds exactly the gates accepting by neither route."""
    rows = (
        universal_flags.Acceptance(gate="a.py", routes=True, declared=()),
        universal_flags.Acceptance(gate="b.py", routes=False, declared=(_FLAG,)),
        universal_flags.Acceptance(gate="c.py", routes=False, declared=()),
    )
    got = universal_flags.lacking(rows)
    if len(got) != 1 or got[0].gate != "c.py":
        out.append(f"selftest: lacking selected {got!r}")
        return 1
    return 0


def an_empty_population_is_unmeasured(out: list[str]) -> int:
    """Check no gates read renders as unmeasured, not as clean."""
    text = universal_flags.render(())
    if "UNMEASURED" not in text:
        out.append(f"selftest: an empty population renders as {text!r}")
        return 1
    return 0


def a_clean_population_names_the_flags(out: list[str]) -> int:
    """Check the closed reading says which flags it measured.

    ⚑ A VERDICT WITHOUT ITS SUBJECT cannot be checked when the authority gains a second flag —
    the reader would say *"all gates accept the universal flags"* about a smaller set than the
    words imply.
    """
    rows = (universal_flags.Acceptance(gate="a.py", routes=True, declared=()),)
    text = universal_flags.render(rows)
    if _FLAG not in text:
        out.append(f"selftest: the clean verdict omits the flag: {text!r}")
        return 1
    return 0


def this_census_agrees_with_the_routing_census(out: list[str]) -> int:
    """Check every gate lacking the flags also fails to route.

    ⚑⚑ NOT A SECOND POPULATION. The corrected figure COLLAPSES onto the routing one: accepting the
    universal flags without also accepting a typo is what the authority provides. Two readers
    disagreeing about the same gates would mean one of them re-derived the property.

    ⚑ THE ROUTING MODULE IS IMPORTED DIRECTLY, not reached through `universal_flags`. A module
    attribute borrowed from another module is the same object at runtime and an unexported name to
    the checker — the re-export defect, refused here before it could be written.
    """
    names = flag_routing.gates()
    unrouted = {row.gate for row in flag_routing.unrouted(flag_routing.population(names))}
    missing = {row.gate for row in universal_flags.lacking(universal_flags.population(names))}
    if not missing <= unrouted:
        out.append(f"selftest: gates lack the flags but route: {sorted(missing - unrouted)!r}")
        return 1
    return 0


_ARMS = (
    routing_through_the_authority_accepts,
    declaring_the_flag_accepts,
    neither_route_is_debt,
    a_handrolled_flag_is_not_acceptance,
    a_routed_gate_reports_its_route,
    the_flag_set_is_read_from_the_authority,
    an_unparseable_gate_yields_nothing,
    an_absent_gate_yields_nothing,
    lacking_selects_only_the_non_accepting,
    an_empty_population_is_unmeasured,
    a_clean_population_names_the_flags,
    this_census_agrees_with_the_routing_census,
)

_CASE_COUNT = 2 + 2 + 1 + 1 + 1 + 2 + 1 + 1 + 1 + 1 + 1 + 1


def selftest() -> int:
    """Run every arm and return an exit code."""
    out: list[str] = []
    failures = sum(arm(out) for arm in _ARMS)

    if failures:
        sys.stderr.write("\n".join(out) + "\n")
        sys.stderr.write(f"universal-flags selftest: {failures} failure(s)\n")
        return 1
    sys.stdout.write(f"universal-flags selftest: {_CASE_COUNT}/{_CASE_COUNT}\n")
    return 0


# ⚑ THE FLAG IS NAMED SO `suite_discovery` SEES THIS SUITE (⟡selftest-discovery).
if __name__ == "__main__":
    sys.exit(selftest() if "--selftest" in sys.argv or len(sys.argv) == 1 else 0)
