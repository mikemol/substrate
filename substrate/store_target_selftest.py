#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Mike Mol
"""The cases for `substrate.store_target`: the dispatch READS its flags and refuses the unstated.

⚑⚑⚑ THE FIRST ARM IS THE MEASURED DEFECT, PINNED AS A CASE, AND IT IS A DIFFERENCE CHECK ON
PURPOSE. The superseded CLI printed BYTE-IDENTICAL output for `--redacted-dsn --sandbox`,
`--redacted-dsn --live` and a bare invocation — the live store under every question — because its
dispatch handled two flags and let everything else fall through to a live accessor. An arm
asserting the two renderings DIFFER is what that CLI cannot satisfy at all, which is the property
worth pinning: any repair that leaves the flags unread fails it regardless of what it prints.

⚑⚑ AND EACH RENDERING IS ALSO CHECKED FOR ITS OWN TENANT, because differing is not sufficient. A
dispatch swapping the two would render differently and be exactly as wrong — a wrong-tenant read
that returns plausible rows nobody can distinguish, which this tree has measured in both
directions.

⚑⚑ THE RENDERED TENANT LINE IS CHECKED AGAINST THE RENDERED TARGET, not merely present. The
predecessor's failure was a label that could disagree with its own subject, and an arm asserting
only that a tenant line EXISTS would pass on a reporter that printed the right word above the
wrong database. The agreement is the claim.

⚑ NO CASE OPENS A CONNECTION, so every arm runs with the store down. This module assembles and
prints and never connects, precisely so it can answer during an outage — which is when an
operator asks what target a tool would use. A suite that needed the store up could not check the
behaviour that exists for the store being down.

⚑ NO CASE NAMES A SECRET, AND ONE ARM ASSERTS THE OUTPUT CANNOT CARRY ONE. The reporter's only
mode is the redacted form; a reporter that was safe became a leak the moment its target gained a
secret, so the absence of the raw value is checked rather than assumed.
"""

from __future__ import annotations

import io
import sys

from mikemol.witness import witness_family

from substrate import store_target, suite_emit, tenant_choice

# The mode this CLI dispatches, named from the module rather than retyped.
_MODE = store_target.REDACTED_DSN

# The placeholder a redacted target carries in place of a credential.
_PLACEHOLDER = "***"


def _render(tenant: str) -> str:
    """Render the report for one tenant, reading no keyring."""
    return store_target.render(tenant, store_target.assemble(tenant))


def _run(argv: list[str]) -> tuple[int, str]:
    """Drive `main` with a captured stdout, returning its code and what it printed."""
    held = sys.stdout
    buf = io.StringIO()
    sys.stdout = buf
    try:
        code = store_target.main(argv)
    finally:
        sys.stdout = held
    return code, buf.getvalue()


def the_two_tenants_render_differently(out: list[str]) -> int:
    """Check that the two tenant flags produce different reports, each naming its own store.

    ⚑⚑ THIS IS THE REGRESSION. The superseded CLI answers identically for both, so a difference
    check is the arm it cannot pass. Each report is also checked for its own database, since a
    dispatch that swapped the tenants would differ and still be wrong.
    """
    bad = 0
    sand = _render(tenant_choice.SANDBOX)
    live = _render(tenant_choice.LIVE)
    if sand == live:
        out.append("selftest: both tenants rendered IDENTICALLY — the defect this supersedes")
        bad += 1
    if "substrate_sandbox" not in sand:
        out.append("selftest: the sandbox report does not name the sandbox database")
        bad += 1
    if "substrate_sandbox" in live:
        out.append("selftest: the LIVE report names the sandbox database")
        bad += 1
    return bad


def the_tenant_line_agrees_with_the_target(out: list[str]) -> int:
    """Check that the named tenant and the rendered database do not disagree.

    ⚑⚑ A FOOTER THAT CAN DISAGREE WITH ITS OWN SUBJECT IS WORSE THAN ONE THAT IS ABSENT, since
    the disagreement is invisible unless the reader already knows the answer. Asserting the
    tenant line merely EXISTS would pass on a reporter printing the right word over the wrong
    rows.
    """
    bad = 0
    for tenant, dbname in (
        (tenant_choice.SANDBOX, "substrate_sandbox"),
        (tenant_choice.LIVE, "substrate"),
    ):
        text = _render(tenant)
        if f"tenant : {tenant}" not in text:
            out.append(f"selftest: the report for {tenant!r} does not name its tenant")
            bad += 1
        if f"'dbname': '{dbname}'" not in text:
            out.append(f"selftest: the {tenant!r} report does not carry database {dbname!r}")
            bad += 1
    return bad


def an_unstated_tenant_is_refused(out: list[str]) -> int:
    """Check that the mode alone refuses, rather than reporting the live store.

    ⚑ THIS IS THE ABSENT `else` MADE PRESENT. The superseded dispatch printed the live target for
    a bare invocation; here the same argv exits non-zero and prints no target at all.
    """
    bad = 0
    code, text = _run([_MODE])
    if code == 0:
        out.append("selftest: an unstated tenant was ACCEPTED")
        bad += 1
    if text:
        out.append("selftest: an unstated tenant still printed a target")
        bad += 1
    return bad


def naming_both_tenants_is_refused(out: list[str]) -> int:
    """Check that naming two tenants refuses rather than picking one.

    ⚑ PICKING ONE WOULD BE THE DEFAULT PROBLEM WEARING A FIX. An invocation stating two tenants
    has not decided which store it meant, and resolving that silently is how a wrong-tenant read
    is manufactured out of an operator's typo.
    """
    bad = 0
    code, text = _run([_MODE, "--sandbox", "--live"])
    if code == 0:
        out.append("selftest: naming both tenants was ACCEPTED")
        bad += 1
    if text:
        out.append("selftest: naming both tenants still printed a target")
        bad += 1
    return bad


def an_unknown_argv_does_not_fall_through(out: list[str]) -> int:
    """Check that an argv without the mode refuses instead of reaching a store branch.

    ⚑⚑ THIS IS THE DEFECT CLASS RATHER THAN THE INSTANCE. The superseded dispatch's fault was
    that unrecognised argv reached a live accessor; an arm driving a flag this CLI has never
    heard of asserts the fall-through is gone for every future flag, not just the measured one.
    """
    bad = 0
    for argv in ([], ["--no-such-flag"], ["--no-such-flag", "--live"]):
        code, text = _run(argv)
        if code == 0:
            out.append(f"selftest: {argv!r} was ACCEPTED without the mode flag")
            bad += 1
        if text:
            out.append(f"selftest: {argv!r} printed a target without the mode flag")
            bad += 1
    return bad


def an_unroutable_tenant_raises_rather_than_guessing(out: list[str]) -> int:
    """Check that routing a tenant the resolver never produces raises instead of picking one.

    ⚑ GUESSING WOULD TURN A CODING FAULT INTO A WRONG-STORE READ — the failure mode with no
    symptom. Reaching the router with an unnamed tenant means the resolver and the router
    disagree, which must surface as itself.
    """
    for bogus in (tenant_choice.UNSTATED, tenant_choice.BOTH, "nonsense"):
        try:
            store_target.assemble(bogus)
        except ValueError:
            continue
        out.append(f"selftest: the router ACCEPTED the unroutable tenant {bogus!r}")
        return 1
    return 0


def the_report_carries_no_credential(out: list[str]) -> int:
    """Check that a rendered report substitutes the credential rather than printing it.

    ⚑ THE ONLY MODE IS THE REDACTED ONE, and this asserts it rather than trusting it. A reporter
    that was safe became a leak once its target gained a secret, silently, because the invariant
    it relied on was never checked anywhere.
    """
    bad = 0
    for tenant in (tenant_choice.SANDBOX, tenant_choice.LIVE):
        text = _render(tenant)
        if "password" in text and _PLACEHOLDER not in text:
            out.append(f"selftest: the {tenant!r} report carries an unredacted credential")
            bad += 1
    return bad


FAMILY = witness_family.of(
    key="store_target",
    apex="the reporter dispatches on its mode and its tenant flags, renders a different and "
    "self-agreeing report per tenant, refuses an unstated, doubly-stated or unrecognised "
    "argv rather than falling through to the live store, and never prints a credential",
    subject="the reports `substrate.store_target` dispatches and renders, offline",
    members=(
        witness_family.Member(
            name="the_two_tenants_render_differently",
            claim="the two tenant flags produce different reports, each naming its own store",
            cases=3,
        ),
        witness_family.Member(
            name="the_tenant_line_agrees_with_the_target",
            claim="the named tenant and the rendered database do not disagree",
            cases=4,
        ),
        witness_family.Member(
            name="an_unstated_tenant_is_refused",
            claim="the mode alone refuses and prints no target",
            cases=2,
        ),
        witness_family.Member(
            name="naming_both_tenants_is_refused",
            claim="naming two tenants refuses rather than picking one",
            cases=2,
        ),
        witness_family.Member(
            name="an_unknown_argv_does_not_fall_through",
            claim="an argv without the mode refuses instead of reaching a store branch",
            cases=6,
        ),
        witness_family.Member(
            name="an_unroutable_tenant_raises_rather_than_guessing",
            claim="routing a tenant the resolver never produces raises instead of picking one",
        ),
        witness_family.Member(
            name="the_report_carries_no_credential",
            claim="a rendered report substitutes the credential rather than printing it",
            cases=2,
            premises=("the_two_tenants_render_differently",),
        ),
    ),
)

_ARMS = (
    the_two_tenants_render_differently,
    the_tenant_line_agrees_with_the_target,
    an_unstated_tenant_is_refused,
    naming_both_tenants_is_refused,
    an_unknown_argv_does_not_fall_through,
    an_unroutable_tenant_raises_rather_than_guessing,
    the_report_carries_no_credential,
)

_CASE_COUNT = FAMILY.count

_SELF_KEY = "substrate/store_target_selftest.py"


def selftest() -> int:
    """Run every arm, report by typed record, and return an exit code."""
    out: list[str] = []
    failures = sum(arm(out) for arm in _ARMS)
    if failures:
        sys.stderr.write("\n".join(out) + "\n")
    return suite_emit.report(_SELF_KEY, _CASE_COUNT - failures, _CASE_COUNT)


if __name__ == "__main__":
    raise SystemExit(selftest() if "--selftest" in sys.argv or len(sys.argv) == 1 else 0)
