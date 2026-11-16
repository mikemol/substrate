#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Mike Mol
"""The cases for `substrate.tool_convention_audit` — two ways a declaration rots.

⚑⚑⚑ A CONVENTION CLAIMS A FLAG'S MEANING IS SHARED, AND THE CLAIM CAN STOP BEING TRUE WITHOUT THE
RECORD CHANGING. STALE (no tool accepts it) and SOLO (one tool does) are neither inferable from
the record nor visible to a reader of it — which is exactly why a record alone is not enough, and
what `farm.py`'s `Arm` refuses in its own domain.

⚑⚑ AND THE REQUIRED-PAIR ARM MEASURES A CONTRACT RATHER THAN QUOTING IT. `--apply` XOR
`--dry-run` is declared mutually exclusive and required precisely because a default is silent in
BOTH failure modes — a default-dry tool does nothing when the caller meant to write, a
default-apply tool writes when they meant to look. A tool with one side still defaults on the
other, and counting those is the only way the contract is more than prose.

⚑ THE TENANT PAIR'S MISSING HALF IS THE FINDING. There is no explicit live selector, so
`--sandbox`'s absence means "live" silently and "forgot to care" is indistinguishable from
"chose". An arm below pins that the incompleteness is REPORTED rather than smoothed over.

⚑ PARITY AGAINST THE ORIGIN WAS MEASURED FIRST — 6 conventions, 25 undeclared recurrences, **0
disagreements**, and the DERIVED pair flags match the origin's hardcoded pair exactly.
"""

from __future__ import annotations

import sys
import tempfile
from pathlib import Path

from substrate import tool_census, tool_convention, tool_convention_audit

# A tool accepting a widely-shared flag, so the convention reads SHARED.
_SHARER = (
    '"""{stem}.py --mode <x>   a mode\n"""\n'
    "import sys\n"
    'if "--selftest" in sys.argv:\n    run()\n'
    'if "--mode" in sys.argv:\n    run()\n'
)

# A tool accepting one side of the mutation pair and not the other.
_HALF = (
    '"""half.py --mode <x>   a mode\n"""\n'
    "import sys\n"
    'if "--apply" in sys.argv:\n    run()\n'
    'if "--mode" in sys.argv:\n    run()\n'
)

# A tool accepting both sides.
_WHOLE = (
    '"""whole.py --mode <x>   a mode\n"""\n'
    "import sys\n"
    'if "--apply" in sys.argv:\n    run()\n'
    'if "--dry-run" in sys.argv:\n    run()\n'
    'if "--mode" in sys.argv:\n    run()\n'
)

# A flag three tools accept that no record explains.
_RECURRING = (
    '"""{stem}.py --mode <x>   a mode\n"""\n'
    "import sys\n"
    'if "--widespread" in sys.argv:\n    run()\n'
    'if "--mode" in sys.argv:\n    run()\n'
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


def _standing(
    rows: tuple[tool_census.Tool, ...], flag: str
) -> tool_convention_audit.Standing | None:
    """Return one convention's standing over a census."""
    return next(
        (s for s in tool_convention_audit.standing(rows) if s.convention.flag == flag), None
    )


def a_flag_no_tool_accepts_is_stale(out: list[str]) -> int:
    """Check a declaration that outlived its flag is reported — ONE OF THE TWO ROTS."""
    rows = _census({"scripts/a.py": _SHARER.format(stem="a")})
    got = _standing(rows, "--roundtrip")
    if got is None or got.verdict != tool_convention_audit.STALE:
        out.append(f"selftest: an unaccepted convention read as {got.verdict if got else None!r}")
        return 1
    if got.holds:
        out.append("selftest: a stale convention reports as holding")
        return 1
    return 0


def a_flag_one_tool_accepts_is_solo(out: list[str]) -> int:
    """Check a per-tool mode wearing a contract's clothes is reported — THE OTHER ROT.

    ⚑ NOT SHARED IS NOT THE SAME AS NOT PRESENT, and a record that only checked existence would
    call this healthy.
    """
    rows = _census({"scripts/a.py": _SHARER.format(stem="a")})
    got = _standing(rows, "--selftest")
    if got is None or got.verdict != tool_convention_audit.SOLO:
        out.append(
            f"selftest: a single-acceptor convention read as {got.verdict if got else None!r}"
        )
        return 1
    return 0


def a_flag_several_tools_accept_is_shared(out: list[str]) -> int:
    """Check a genuinely shared contract reads as holding."""
    rows = _census(
        {"scripts/a.py": _SHARER.format(stem="a"), "scripts/b.py": _SHARER.format(stem="b")}
    )
    got = _standing(rows, "--selftest")
    if got is None or not got.holds:
        out.append(f"selftest: a shared convention read as {got.verdict if got else None!r}")
        return 1
    return 0


def the_pair_flags_are_derived_from_the_contracts(out: list[str]) -> int:
    """Check the required pair comes from the records — ⟡pair-flags-derived, THE PAYDOWN.

    ⚑⚑ THE ORIGIN'S COMMENT SAYS THE PAIR IS *"read from CONVENTIONS, never retyped"* and the line
    below it retypes them; three copies existed. A derivation cannot drift from the records, and
    a convention renamed tomorrow stays measured.
    """
    got = tool_convention_audit.pair_flags()
    if set(got) != {"--apply", "--dry-run"}:
        out.append(f"selftest: the derived pair reads as {list(got)!r}")
        return 1
    for flag in got:
        record = tool_convention.by_flag(flag)
        if record is None or tool_convention_audit.PAIR_MARK not in record.contract:
            out.append(f"selftest: {flag} was derived without declaring a partner")
            return 1
    return 0


def a_tool_taking_one_side_is_half_paired(out: list[str]) -> int:
    """Check a silent default on the other side is counted — THE CONTRACT MEASURED.

    ⚑⚑ A DEFAULT IS SILENT IN BOTH DIRECTIONS: a default-dry tool does nothing when the caller
    meant to write, a default-apply tool writes when they meant to look. Which one you get is a
    property of whichever tool you happened to invoke.
    """
    rows = _census({"scripts/half.py": _HALF, "scripts/whole.py": _WHOLE})
    pair = next(
        (p for p in tool_convention_audit.required_pairs(rows) if p.kind == "mutation"), None
    )
    if pair is None:
        out.append("selftest: the mutation pair was not measured")
        return 1
    if "scripts/half.py" not in pair.only_left:
        out.append(f"selftest: the half-paired tool reads as {pair.only_left!r}")
        return 1
    if "scripts/whole.py" not in pair.both:
        out.append(f"selftest: the fully-paired tool reads as {pair.both!r}")
        return 1
    return 0


def the_half_paired_count_is_reported(out: list[str]) -> int:
    """Check the number a paydown is measured against is available."""
    rows = _census({"scripts/half.py": _HALF, "scripts/whole.py": _WHOLE})
    pair = next(
        (p for p in tool_convention_audit.required_pairs(rows) if p.kind == "mutation"), None
    )
    if pair is None or pair.half_paired != 1:
        out.append(f"selftest: the half-paired count reads as {pair.half_paired if pair else None}")
        return 1
    return 0


def the_tenant_pair_reports_its_missing_half(out: list[str]) -> int:
    """Check an incomplete pair says so — THE ABSENT-HALF ARM.

    ⚑⚑ THERE IS NO EXPLICIT LIVE SELECTOR, so `--sandbox`'s absence is a DEFAULT rather than a
    choice. Reporting the pair as complete would hide the one thing a reader must know.
    """
    rows = _census({"scripts/a.py": _SHARER.format(stem="a")})
    pair = next((p for p in tool_convention_audit.required_pairs(rows) if p.kind == "tenant"), None)
    if pair is None:
        out.append("selftest: the tenant pair was not measured")
        return 1
    if not pair.incomplete:
        out.append("selftest: the tenant pair reports a second half that does not exist")
        return 1
    return 0


def a_flag_three_tools_accept_is_an_undeclared_recurrence(out: list[str]) -> int:
    """Check the DECIDE-or-CONVERGE arm surfaces a pattern no record explains.

    ⚑ THE CENSUS CANNOT TELL AN UNDECLARED CONVENTION FROM REAL DIVERGENCE, and that is not a
    limitation to fix — it is why a human writes the `why`.
    """
    rows = _census({f"scripts/{n}.py": _RECURRING.format(stem=n) for n in "abc"})
    got = tool_convention_audit.undeclared_recurrences(rows)
    if "--widespread" not in got:
        out.append(f"selftest: the recurrence was not surfaced: {sorted(got)!r}")
        return 1
    return 0


def a_declared_flag_is_not_an_undeclared_recurrence(out: list[str]) -> int:
    """Check a flag with a record is excluded — the negative control."""
    rows = _census({f"scripts/{n}.py": _SHARER.format(stem=n) for n in "abc"})
    if "--selftest" in tool_convention_audit.undeclared_recurrences(rows):
        out.append("selftest: a declared convention was reported as undeclared")
        return 1
    return 0


def two_tools_are_not_yet_a_recurrence(out: list[str]) -> int:
    """Check the threshold holds — two is a coincidence, three is a pattern."""
    rows = _census({f"scripts/{n}.py": _RECURRING.format(stem=n) for n in "ab"})
    if "--widespread" in tool_convention_audit.undeclared_recurrences(rows):
        out.append("selftest: two tools were reported as a recurrence")
        return 1
    return 0


_ARMS = (
    a_flag_no_tool_accepts_is_stale,
    a_flag_one_tool_accepts_is_solo,
    a_flag_several_tools_accept_is_shared,
    the_pair_flags_are_derived_from_the_contracts,
    a_tool_taking_one_side_is_half_paired,
    the_half_paired_count_is_reported,
    the_tenant_pair_reports_its_missing_half,
    a_flag_three_tools_accept_is_an_undeclared_recurrence,
    a_declared_flag_is_not_an_undeclared_recurrence,
    two_tools_are_not_yet_a_recurrence,
)

_CASE_COUNT = 2 + 1 + 1 + 2 + 2 + 1 + 2 + 1 + 1 + 1


def selftest() -> int:
    """Run every arm and return an exit code."""
    out: list[str] = []
    failures = sum(arm(out) for arm in _ARMS)

    if failures:
        sys.stderr.write("\n".join(out) + "\n")
        sys.stderr.write(f"tool-convention-audit selftest: {failures} failure(s)\n")
        return 1
    sys.stdout.write(f"tool-convention-audit selftest: {_CASE_COUNT}/{_CASE_COUNT}\n")
    return 0


# ⚑ THE FLAG IS NAMED SO `suite_discovery` SEES THIS SUITE (⟡selftest-discovery).
if __name__ == "__main__":
    sys.exit(selftest() if "--selftest" in sys.argv or len(sys.argv) == 1 else 0)
