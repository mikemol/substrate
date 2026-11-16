# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Mike Mol
"""The cases for `substrate.md_lint_audit` — five verdicts, and the boundaries between them.

⚑⚑⚑ THE `unearned` ARM IS THE SUBJECT. A disabled rule that fires zero times is an exemption
nobody is paying for, and it survives precisely because nothing asks — measured, two of four rules
in this project's first config were exactly that. A suite exercising only the earned case would
pass against an audit that never reported decoration at all.

⚑⚑ AND THE PAYDOWN BOUNDARY IS ASSERTED FROM BOTH SIDES. At the threshold a rule is fixable
content; one past it the exemption is load-bearing. Testing one side alone leaves the comparison
free to be off by one in the direction that quietly justifies an exemption.

⚑ THE `live` ARM IS WHAT STOPS A CLEAN BILL. Without rows for firing rules the config never
mentions, the audit answers only *are my exemptions justified* and reads as clean for a corpus full
of findings.
"""

from __future__ import annotations

import sys

from substrate import md_lint_audit as mla

#: How many documents the fixtures pretend to have walked. Named because every detail string
#: carries it, and a denominator is what makes a zero mean something.
DOCUMENTS = 4

#: A count comfortably past the paydown threshold — an exemption that is load-bearing.
MANY = mla.PAYDOWN_MAX + 10


def _unearned_cases() -> list[tuple[str, bool]]:
    """Return `(label, passed)` for the decoration the audit exists to find."""
    out: list[tuple[str, bool]] = []
    rows = mla.audit({"MD033": False}, {}, DOCUMENTS)

    out.append(
        (
            f"a disabled rule firing zero times is unearned: {rows[0].why()}",
            rows[0].verdict == "unearned",
        )
    )
    out.append((f"and the detail says delete it: {rows[0].detail}", "delete it" in rows[0].detail))
    # ⚑ THE DENOMINATOR IS IN THE DETAIL. Zero findings over zero documents is a fact about the
    # run, so a reader must be told which they are looking at.
    out.append(
        (
            f"and it carries the denominator: {rows[0].detail}",
            f"{DOCUMENTS} document" in rows[0].detail,
        )
    )
    return out


def _paydown_cases() -> list[tuple[str, bool]]:
    """Return `(label, passed)` for the boundary between fixable and load-bearing.

    ⚑⚑ BOTH SIDES ARE ASSERTED. A one-sided arm lets the comparison drift in the direction that
    turns a fixable finding into a permanent exemption, which is the failure the whole verdict
    scheme exists to prevent.
    """
    out: list[tuple[str, bool]] = []

    at = mla.audit({"MD032": False}, {"MD032": mla.PAYDOWN_MAX}, DOCUMENTS)
    out.append((f"at the threshold it is paydown: {at[0].why()}", at[0].verdict == "paydown"))
    out.append(
        (
            f"and the detail says fix the document: {at[0].detail}",
            "FIX in the document" in at[0].detail,
        )
    )

    past = mla.audit({"MD032": False}, {"MD032": mla.PAYDOWN_MAX + 1}, DOCUMENTS)
    out.append((f"one past it is earned: {past[0].why()}", past[0].verdict == "earned"))

    # ⚑ THE SENSITIVITY ARM. Raising ONLY the threshold must move the verdict, or the parameter is
    # not consulted and the boundary is incidental.
    raised = mla.audit(
        {"MD032": False}, {"MD032": mla.PAYDOWN_MAX + 1}, DOCUMENTS, paydown_max=mla.PAYDOWN_MAX + 1
    )
    out.append(
        (
            f"raising ONLY the threshold moves it: {raised[0].verdict}",
            raised[0].verdict == "paydown",
        )
    )
    return out


def _earned_cases() -> list[tuple[str, bool]]:
    """Return `(label, passed)` for an exemption that is genuinely load-bearing."""
    out: list[tuple[str, bool]] = []
    rows = mla.audit({"MD041": False}, {"MD041": MANY}, DOCUMENTS)

    out.append(
        (f"a heavily-firing disabled rule is earned: {rows[0].why()}", rows[0].verdict == "earned")
    )
    out.append((f"and the count is in the detail: {rows[0].detail}", f"{MANY}x" in rows[0].detail))
    return out


def _configured_cases() -> list[tuple[str, bool]]:
    """Return `(label, passed)` for a rule given a value rather than turned off.

    ⚑ AN AGREEMENT IS NOT A SUPPRESSION, and conflating them is what made a width setting look
    like an exemption. A configured rule that still fires is reported with its remaining findings.
    """
    out: list[tuple[str, bool]] = []
    rows = mla.audit({"MD013": {"line_length": 120}}, {"MD013": 2}, DOCUMENTS)

    out.append(
        (
            f"a valued rule is configured, not disabled: {rows[0].why()}",
            rows[0].verdict == "configured",
        )
    )
    out.append(
        (f"and its remaining findings are named: {rows[0].detail}", "2 finding" in rows[0].detail)
    )

    # ⚑ AND `False` IS THE ONLY DISABLE. A truthy value is a setting, never an exemption.
    enabled = mla.audit({"MD013": True}, {}, DOCUMENTS)
    out.append(
        (
            f"an enabled rule is not unearned: {enabled[0].verdict}",
            enabled[0].verdict == "configured",
        )
    )
    return out


def _live_cases() -> list[tuple[str, bool]]:
    """Return `(label, passed)` for firing rules the config never mentions.

    ⚑⚑⚑ WITHOUT THESE THE AUDIT READS AS A CLEAN BILL. A config with one justified exemption and a
    corpus with four hundred findings in unmentioned rules would report entirely green.
    """
    out: list[tuple[str, bool]] = []
    rows = mla.audit({"MD041": False}, {"MD041": MANY, "MD013": 7}, DOCUMENTS)

    live = mla.by_verdict(rows, "live")
    out.append(
        (
            f"an unmentioned firing rule is reported: {[r.rule for r in live]}",
            [r.rule for r in live] == ["MD013"],
        )
    )
    out.append((f"and named as real debt: {live[0].detail}", "real debt" in live[0].detail))

    # ⚑ A RULE MENTIONED IN THE CONFIG IS NEVER ALSO LIVE — otherwise every exemption is
    # double-counted and the summary overstates the debt.
    out.append(
        (
            f"and a mentioned rule is not duplicated: {[r.rule for r in rows]}",
            [r.rule for r in rows].count("MD041") == 1,
        )
    )
    return out


def _shape_cases() -> list[tuple[str, bool]]:
    """Return `(label, passed)` for what the audit must not claim."""
    out: list[tuple[str, bool]] = []

    out.append(
        (
            f"an empty config and no findings yields nothing: {mla.audit({}, {}, 0)}",
            mla.audit({}, {}, 0) == [],
        )
    )

    # ⚑ SCHEMA METADATA IS NOT A RULE. A `$schema` key reported as an unearned exemption is a false
    # row in the column a reader is meant to act on.
    meta = mla.audit({"$schema": "https://example/schema.json"}, {}, DOCUMENTS)
    out.append((f"a metadata key is not audited: {meta}", meta == []))
    return out


def _summary_cases() -> list[tuple[str, bool]]:
    """Return `(label, passed)` for the summary line and its denominator."""
    out: list[tuple[str, bool]] = []
    rows = mla.audit({"MD033": False, "MD041": False}, {"MD041": MANY}, DOCUMENTS)

    line = mla.summarise(rows, DOCUMENTS)
    out.append(
        (
            f"the summary names each class present: {line}",
            "1 unearned" in line and "1 earned" in line,
        )
    )
    out.append((f"and carries the document count: {line}", f"{DOCUMENTS} document" in line))
    out.append(
        (
            f"and an empty audit says so: {mla.summarise([], 0)}",
            "no rules audited" in mla.summarise([], 0),
        )
    )
    return out


def selftest() -> bool:
    """Run every case, reporting failures by name."""
    cases = (
        _unearned_cases()
        + _paydown_cases()
        + _earned_cases()
        + _configured_cases()
        + _live_cases()
        + _shape_cases()
        + _summary_cases()
    )
    ok = sum(1 for _, passed in cases if passed)
    for label, passed in cases:
        if not passed:
            print(f"  FAIL {label}")  # noqa: T201
    print(f"md-lint-audit selftest: {ok}/{len(cases)}")  # noqa: T201
    return ok == len(cases)


# ⚑ THE FLAG IS NAMED SO `run_selftests.discover()` SEES THIS SUITE (⟡selftest-discovery).
if __name__ == "__main__":
    if "--selftest" in sys.argv or len(sys.argv) == 1:
        raise SystemExit(0 if selftest() else 1)
    raise SystemExit(0)
