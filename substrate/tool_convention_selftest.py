#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Mike Mol
"""The cases for `substrate.tool_convention` — an invoker, never a count.

⚑⚑⚑ THE `--top` ARM IS THE ITEM, AND IT GUARDS AGAINST THIS SESSION'S OWN TEMPTATION.
`substrate/page.py` was built here to bound listings, and `--top` was chosen over `--limit`
because the census reports it on NINE tools against one. That is exactly the popularity signal
the record shape refuses: nothing INVOKES `--top`, so it is recurrence, not convention. An arm
below asserts it stays undeclared — because the author most likely to bless a flag on a count is
the one who just spent a session converging on its spelling.

⚑⚑ COUNTING CANNOT SEPARATE A CONVENTION FROM A COINCIDENCE, and the origin's fixture says why: a
`--hidden` on 2 of 3 tools is a MAJORITY and emphatically not one. So every record carries an
invoker — the structural warrant — and two of the six carry a named DISCIPLINE instead of a
dispatcher, which is permitted precisely because it is argued rather than assumed.

⚑ PARITY AGAINST THE ORIGIN WAS MEASURED FIRST — **6 conventions, 0 disagreements** on the
declared records and on the computed universal set, the latter over a census 12 tools wider.
"""

from __future__ import annotations

import sys

from substrate import tool_convention

# The flag whose invoker is a real dispatcher.
_DISPATCHED = "--selftest"

# A flag whose warrant is a named discipline rather than a runner.
_DISCIPLINED = "--apply"

# The pair this session built and deliberately did not declare.
_PAGING = ("--top", "--skip")

# A flag no tool accepts, for the membership control.
_ABSENT = "--nonesuch"

# Fixture accept-sets: one flag unanimous, one on a majority.
_UNANIMOUS = "--everywhere"
_MAJORITY = "--hidden"
_ACCEPTED = (
    frozenset({_UNANIMOUS, _MAJORITY}),
    frozenset({_UNANIMOUS, _MAJORITY}),
    frozenset({_UNANIMOUS}),
)


def every_record_names_an_invoker(out: list[str]) -> int:
    """Check no convention is declared without a warrant.

    ⚑ THE FIELD IS THE CLAIM'S FALSIFIER. A convention whose invoker stops invoking is STALE, the
    way an `Arm` that stops biting is VACUOUS — and a record with an empty invoker cannot go stale
    because it never said anything checkable.
    """
    for convention in tool_convention.CONVENTIONS:
        if not convention.invoker.strip():
            out.append(f"selftest: {convention.flag} declares no invoker")
            return 1
        if not convention.why.strip():
            out.append(f"selftest: {convention.flag} carries no argument")
            return 1
    return 0


def a_dispatcher_invoker_is_a_module(out: list[str]) -> int:
    """Check the runner-backed record names something runnable."""
    got = tool_convention.by_flag(_DISPATCHED)
    if got is None or ".py" not in got.invoker:
        out.append(f"selftest: {_DISPATCHED}'s invoker reads as {got!r}")
        return 1
    return 0


def a_discipline_invoker_says_it_is_one(out: list[str]) -> int:
    """Check a record with no dispatcher SAYS so rather than leaving the field thin.

    ⚑⚑ A DISCIPLINE COUNTS, BUT ONLY WHEN NAMED. `(none — the writers' shared discipline)` is a
    claim a reader can weigh; a blank invoker is a popularity argument with the evidence removed.
    """
    got = tool_convention.by_flag(_DISCIPLINED)
    if got is None or "none" not in got.invoker.lower():
        out.append(f"selftest: {_DISCIPLINED}'s invoker reads as {got!r}")
        return 1
    if "—" not in got.invoker and "-" not in got.invoker:
        out.append(f"selftest: {_DISCIPLINED} names no discipline: {got.invoker!r}")
        return 1
    return 0


def the_paging_pair_is_not_declared(out: list[str]) -> int:
    """Check `--top`/`--skip` stay undeclared — THE ITEM.

    ⚑⚑⚑ NINE TOOLS ACCEPT `--top`, WHICH IS WHY IT IS TEMPTING AND WHY IT MUST NOT BE DECLARED.
    Nothing dispatches it: `page` is a library a tool opts into, not a runner. Declaring it on a
    count would turn this list into a tally of what recurs — the frozen-vocabulary shape every
    entry here was written to avoid.

    ⚑ IT MAY EARN A RECORD LATER, when a runner dispatches it or the pair becomes a stated
    obligation on listing modes. This arm fails the day someone declares it without that, which
    is the point.
    """
    for flag in _PAGING:
        if flag in tool_convention.HARNESS_CONTRACTS:
            out.append(f"selftest: {flag} was declared a convention on recurrence alone")
            return 1
    return 0


def the_flags_set_is_derived(out: list[str]) -> int:
    """Check the membership set is a projection of the records, not a second list.

    ⚑ A SECOND LIST IS THE FROZEN-ROSTER SHAPE. Every reader wants membership, so the set is
    retained — but the records are the authority, and the two cannot disagree if one is computed
    from the other.
    """
    expected = {convention.flag for convention in tool_convention.CONVENTIONS}
    if set(tool_convention.HARNESS_CONTRACTS) != expected:
        out.append("selftest: the flag set is not a projection of the records")
        return 1
    return 0


def an_undeclared_flag_resolves_to_nothing(out: list[str]) -> int:
    """Check the lookup refuses rather than inventing."""
    if tool_convention.by_flag(_ABSENT) is not None:
        out.append(f"selftest: {_ABSENT} resolved to a convention")
        return 1
    return 0


def a_unanimous_flag_is_universal(out: list[str]) -> int:
    """Check the measured arm still reports what every tool accepts."""
    got = tool_convention.universal(_ACCEPTED)
    if _UNANIMOUS not in got:
        out.append(f"selftest: a unanimous flag was not universal: {sorted(got)!r}")
        return 1
    return 0


def a_majority_flag_is_not_universal(out: list[str]) -> int:
    """Check a majority is not enough — THE FIXTURE THE ORIGIN NAMES.

    ⚑⚑ `--hidden` ON 2 OF 3 TOOLS IS A MAJORITY AND EMPHATICALLY NOT A CONVENTION. A share
    threshold would admit it, which is why the measured arm is a strict intersection and the rest
    comes from declared records.
    """
    got = tool_convention.universal(_ACCEPTED)
    if _MAJORITY in got:
        out.append(f"selftest: a majority flag was reported universal: {sorted(got)!r}")
        return 1
    return 0


def a_declared_contract_survives_a_thin_intersection(out: list[str]) -> int:
    """Check a convention is not lost when one tool stops accepting it.

    ⚑⚑ THE INTERSECTION WAS PASSING ON BORROWED EVIDENCE, AND CLOSING A LEAK EXPOSED IT. When the
    import walk stopped leaking a CLI sibling's flags, the strict intersection reported ZERO
    conventions — correctly, and uselessly. The declared arm is what keeps `--selftest` universal
    when only some tools spell it themselves.
    """
    accepted = (frozenset({_DISPATCHED}), frozenset({"--other"}))
    if _DISPATCHED not in tool_convention.universal(accepted):
        out.append("selftest: a declared contract was lost to a thin intersection")
        return 1
    return 0


def an_empty_population_is_not_universal(out: list[str]) -> int:
    """Check no tools yields no conventions rather than raising.

    ⚑ `frozenset.intersection()` OF NOTHING IS AN ERROR, not an empty set — and a census over an
    empty tree is a state a borrowing checkout reaches.
    """
    if tool_convention.universal(()):
        out.append("selftest: an empty population reported conventions")
        return 1
    return 0


_ARMS = (
    every_record_names_an_invoker,
    a_dispatcher_invoker_is_a_module,
    a_discipline_invoker_says_it_is_one,
    the_paging_pair_is_not_declared,
    the_flags_set_is_derived,
    an_undeclared_flag_resolves_to_nothing,
    a_unanimous_flag_is_universal,
    a_majority_flag_is_not_universal,
    a_declared_contract_survives_a_thin_intersection,
    an_empty_population_is_not_universal,
)

_CASE_COUNT = 2 + 1 + 2 + 2 + 1 + 1 + 1 + 1 + 1 + 1


def selftest() -> int:
    """Run every arm and return an exit code."""
    out: list[str] = []
    failures = sum(arm(out) for arm in _ARMS)

    if failures:
        sys.stderr.write("\n".join(out) + "\n")
        sys.stderr.write(f"tool-convention selftest: {failures} failure(s)\n")
        return 1
    sys.stdout.write(f"tool-convention selftest: {_CASE_COUNT}/{_CASE_COUNT}\n")
    return 0


# ⚑ THE FLAG IS NAMED SO `suite_discovery` SEES THIS SUITE (⟡selftest-discovery).
if __name__ == "__main__":
    sys.exit(selftest() if "--selftest" in sys.argv or len(sys.argv) == 1 else 0)
