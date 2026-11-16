#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Mike Mol
"""The cases for `substrate.parity` — the three states, and why collapsing one is the defect.

⚑⚑⚑ THE `UNMEASURED` ARMS ARE THE ITEM. A probe that cannot load its origin and reports zero
disagreements is INDISTINGUISHABLE from a clean comparison, and gets banked as one. That is the
`census-green-is-a-fact-about-the-census` shape applied to the instrument built to catch it, so
the state is separate, the exit code is separate, and the reason travels with it.

⚑⚑ AND THE WIDENING ARM IS THE ONE THAT COST THREE FALSE DISAGREEMENTS. An extraction usually
widens what the reader can see; rows under the new prefix exist on one side only and are the
INTENDED CHANGE. Comparing over the union reports the widening as a regression — measured, three
times in one session, out of five disagreements found.

⚑ THE VALUE COMPARISON IS PINNED SEPARATELY FROM THE KEY COMPARISON, because two censuses can
hold identical keys and opposite verdicts: `FIXTURE` and `UNDOCUMENTED` are the same row with
different consequences, and a key-only check calls that agreement.
"""

from __future__ import annotations

import sys

from substrate import parity

# Two censuses that agree, and one that does not.
_LEFT = {"a": "ok", "b": "ok"}
_RIGHT = {"a": "ok", "b": "ok"}
_CLASHING = {"a": "ok", "b": "REFUSED"}

# A prefix the origin structurally cannot see.
_WIDENED = "substrate/"


def agreement_reports_no_disagreements(out: list[str]) -> int:
    """Check two identical readings compare as AGREED."""
    got = parity.compare([parity.differing_keys("k", _LEFT, _RIGHT)], population=2)
    if got.state != parity.AGREED:
        out.append(f"selftest: identical readings compared as {got.state}")
        return 1
    if got.exit_code != 0:
        out.append(f"selftest: agreement exits {got.exit_code}")
        return 1
    return 0


def a_membership_difference_is_reported(out: list[str]) -> int:
    """Check a key present on one side only is named, and on which side."""
    row = parity.differing_keys("keys", ["a", "b"], ["a", "c"])
    if row is None:
        out.append("selftest: a membership difference was not reported")
        return 1
    if row.only_origin != ("b",) or row.only_new != ("c",):
        out.append(f"selftest: the sides are {row.only_origin!r} / {row.only_new!r}")
        return 1
    return 0


def a_value_difference_is_reported(out: list[str]) -> int:
    """Check identical keys with different values are caught — THE VERDICT ARM.

    ⚑⚑ `FIXTURE` AND `UNDOCUMENTED` ARE THE SAME ROW WITH OPPOSITE CONSEQUENCES. A key-only
    comparison reports agreement on a census whose verdicts have inverted.
    """
    row = parity.differing_values("kinds", _LEFT, _CLASHING)
    if row is None:
        out.append("selftest: a value difference was not reported")
        return 1
    if "b=ok" not in row.only_origin or "b=REFUSED" not in row.only_new:
        out.append(f"selftest: the values are {row.only_origin!r} / {row.only_new!r}")
        return 1
    return 0


def identical_values_are_not_reported(out: list[str]) -> int:
    """Check agreeing values produce no row — the discriminator for the arm above."""
    if parity.differing_values("kinds", _LEFT, _RIGHT) is not None:
        out.append("selftest: identical values were reported as differing")
        return 1
    return 0


def the_shared_population_excludes_the_widening(out: list[str]) -> int:
    """Check rows under a widened prefix are excluded — THE THREE-FALSE-POSITIVES ARM.

    ⚑⚑⚑ AN EXTRACTION USUALLY WIDENS WHAT THE READER SEES, and those rows exist on one side by
    design. Comparing over the union reports the intended change as a regression; measured three
    times in one session out of five disagreements found.
    """
    got = parity.shared(
        ["scratch/a.py", "substrate/b.py"],
        ["scratch/a.py", "substrate/b.py", "substrate/c.py"],
        widened=_WIDENED,
    )
    if got != frozenset({"scratch/a.py"}):
        out.append(f"selftest: the shared population is {sorted(got)!r}")
        return 1
    return 0


def the_shared_population_is_an_intersection(out: list[str]) -> int:
    """Check a key missing from either side is excluded even without a widening prefix."""
    got = parity.shared(["a", "b"], ["b", "c"])
    if got != frozenset({"b"}):
        out.append(f"selftest: the intersection is {sorted(got)!r}")
        return 1
    return 0


def an_unmeasured_run_is_not_agreement(out: list[str]) -> int:
    """Check an unreachable origin reports UNMEASURED — THE DANGEROUS ARM.

    ⚑⚑⚑ ZERO DISAGREEMENTS FROM A PROBE THAT NEVER RAN is indistinguishable from a clean
    comparison, and banked as one. The state, the exit code and the reason are all separate so
    that cannot happen silently.
    """
    got = parity.unmeasured("the origin could not be imported")
    if got.state != parity.UNMEASURED:
        out.append(f"selftest: an unreachable origin reported {got.state}")
        return 1
    if got.exit_code == 0:
        out.append("selftest: an unmeasured run exits 0 — indistinguishable from agreement")
        return 1
    if not got.disagreements:
        rendered = got.render()
        if "NOT agreement" not in rendered:
            out.append("selftest: the render does not say it is not agreement")
            return 1
    return 0


def the_unmeasured_reason_travels(out: list[str]) -> int:
    """Check the reason reaches the reader.

    ⚑ *"could not be imported"* and *"has no such attribute"* send a reader to different places;
    a bare UNMEASURED sends them to neither.
    """
    got = parity.unmeasured("no such attribute")
    if "no such attribute" not in got.render():
        out.append("selftest: the reason did not reach the render")
        return 1
    return 0


def the_three_states_have_three_exit_codes(out: list[str]) -> int:
    """Check no two states share an exit code."""
    codes = {parity.CODES[state] for state in (parity.AGREED, parity.DIFFERING, parity.UNMEASURED)}
    expected = 3
    if len(codes) != expected:
        out.append(f"selftest: the three states use {len(codes)} distinct code(s)")
        return 1
    return 0


def a_disagreement_is_evidence_not_a_verdict(out: list[str]) -> int:
    """Check the render says a disagreement may be the probe's own defect.

    ⚑⚑ THREE OF FIVE DISAGREEMENTS IN ONE SESSION were probe defects or intended changes. A
    report that reads as a verdict invites acting on the wrong half.
    """
    row = parity.differing_keys("keys", ["a"], ["b"])
    got = parity.compare([row], population=1)
    if "EVIDENCE, NOT A VERDICT" not in got.render():
        out.append("selftest: the render presents a disagreement as a verdict")
        return 1
    return 0


def a_none_row_is_dropped(out: list[str]) -> int:
    """Check agreeing comparisons contribute no rows."""
    got = parity.compare([None, None], population=5)
    if got.disagreements:
        out.append(f"selftest: {len(got.disagreements)} row(s) from agreeing comparisons")
        return 1
    return 0


def the_population_is_reported(out: list[str]) -> int:
    """Check the denominator reaches the reader — a hit count needs one."""
    got = parity.compare([], population=42)
    if "42 shared item(s)" not in got.render():
        out.append("selftest: the population is absent from the render")
        return 1
    return 0


_ARMS = (
    agreement_reports_no_disagreements,
    a_membership_difference_is_reported,
    a_value_difference_is_reported,
    identical_values_are_not_reported,
    the_shared_population_excludes_the_widening,
    the_shared_population_is_an_intersection,
    an_unmeasured_run_is_not_agreement,
    the_unmeasured_reason_travels,
    the_three_states_have_three_exit_codes,
    a_disagreement_is_evidence_not_a_verdict,
    a_none_row_is_dropped,
    the_population_is_reported,
)

_CASE_COUNT = 2 + 2 + 2 + 1 + 1 + 1 + 3 + 1 + 1 + 1 + 1 + 1


def selftest() -> int:
    """Run every arm and return an exit code."""
    out: list[str] = []
    failures = sum(arm(out) for arm in _ARMS)

    if failures:
        sys.stderr.write("\n".join(out) + "\n")
        sys.stderr.write(f"parity selftest: {failures} failure(s)\n")
        return 1
    sys.stdout.write(f"parity selftest: {_CASE_COUNT}/{_CASE_COUNT}\n")
    return 0


# ⚑ THE FLAG IS NAMED SO `suite_discovery` SEES THIS SUITE (⟡selftest-discovery).
if __name__ == "__main__":
    sys.exit(selftest() if "--selftest" in sys.argv or len(sys.argv) == 1 else 0)
