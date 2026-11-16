#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Mike Mol
"""The cases for `substrate.tenant_choice`: a flag is READ, and an unnamed tenant is REFUSED.

⚑⚑⚑ THE FIRST ARM IS THE MEASURED DEFECT, PINNED AS A CASE. `jea/metalanguage/store.py`'s CLI
prints byte-identical output for `--redacted-dsn --sandbox`, `--redacted-dsn --live` and a bare
invocation — the LIVE store's name under all three, because its dispatch handles two flags and
lets every other argv fall through to a live accessor. The arm that separates the two tenants is
what makes that silence loud at the layer where it is cheap: it asserts the two argvs resolve
DIFFERENTLY, which is the property the shipped CLI does not have.

⚑⚑ AND ASSERTING THE ANSWERS DIFFER IS NOT THE SAME AS ASSERTING EACH ANSWER, so both are here.
A resolver that returned a distinct wrong tenant for each flag would satisfy a difference check
while being useless; one that returned the right answer for `--sandbox` only would satisfy a
single-value check while reproducing the defect for the other half. The pair is the discriminator.

⚑⚑ THE TWO REFUSALS ARE CHECKED SEPARATELY AND CHECKED TO BE DISTINCT. `unstated` and `both` are
different operator mistakes with different repairs — add a flag versus remove one — so an arm
asserting only that each is "not named" would pass on a resolver that collapsed them into one
answer. The distinctness is the claim, not the refusal.

⚑ EVERY CASE RUNS OFFLINE, WITH NO STORE, NO KEYRING AND NO DRIVER, which is the property the
module was split out to have. The decision is pure and total over a list of strings; a suite that
needed postgres up to read a tenant flag would be asserting the store's availability rather than
the rule, and would go unrun exactly when the store is the thing that broke.

⚑ THE FLAG SPELLINGS ARE NAMED FROM THE MODULE, NEVER RETYPED. A case spelling `"--sandbox"`
independently would keep passing while the module and its consumers disagreed, which is the
second-spelling drift this whole arc is paying down.
"""

from __future__ import annotations

import io
import sys

from mikemol.witness import witness_family

from substrate import suite_emit, tenant_choice

# The flag that names each tenant, read from the module rather than retyped.
_SANDBOX_FLAG = "--sandbox"
_LIVE_FLAG = "--live"

# A mode flag that travels beside a tenant flag. ⚑ IT IS DELIBERATELY UNKNOWN TO THE RESOLVER:
# the defect under test is a dispatch that ignored flags it did not recognise, so the cases drive
# argvs that carry one.
_MODE_FLAG = "--redacted-dsn"


def the_two_tenant_flags_resolve_differently(out: list[str]) -> int:
    """Check that `--sandbox` and `--live` produce different answers, and the right ones.

    ⚑⚑ THIS IS THE REGRESSION. The CLI this replaces answers identically for both, so an arm
    that only checked one flag would pass against it. Both the difference and each value are
    asserted: a resolver returning two distinct wrong tenants would satisfy the first alone.
    """
    bad = 0
    sand = tenant_choice.resolve([_MODE_FLAG, _SANDBOX_FLAG]).tenant
    live = tenant_choice.resolve([_MODE_FLAG, _LIVE_FLAG]).tenant
    if sand == live:
        out.append(f"selftest: both tenant flags resolved to {sand!r} — the defect this replaces")
        bad += 1
    if sand != tenant_choice.SANDBOX:
        out.append(f"selftest: {_SANDBOX_FLAG} resolved to {sand!r}, want the sandbox")
        bad += 1
    if live != tenant_choice.LIVE:
        out.append(f"selftest: {_LIVE_FLAG} resolved to {live!r}, want the live store")
        bad += 1
    return bad


def an_unstated_tenant_is_refused_not_defaulted(out: list[str]) -> int:
    """Check that naming no tenant refuses, rather than quietly meaning the live store.

    ⚑ A DEFAULT WOULD MAKE FORGETTING INDISTINGUISHABLE FROM CHOOSING, which is the operator
    ruling this resolver exists to hold. The arm asserts both that the answer is `unstated` and
    that it is NOT the live store — the specific silent branch the flags were added to remove.
    """
    bad = 0
    choice = tenant_choice.resolve([_MODE_FLAG])
    if choice.tenant != tenant_choice.UNSTATED:
        out.append(f"selftest: a bare argv resolved to {choice.tenant!r}, want unstated")
        bad += 1
    if choice.tenant == tenant_choice.LIVE:
        out.append("selftest: an unstated tenant DEFAULTED to live — the silent branch is back")
        bad += 1
    if choice.named:
        out.append("selftest: an unstated tenant reported itself as named")
        bad += 1
    return bad


def naming_both_tenants_is_its_own_refusal(out: list[str]) -> int:
    """Check that naming two tenants refuses, and refuses DIFFERENTLY from naming none.

    ⚑⚑ THE DISTINCTNESS IS THE CLAIM. Both are refusals, but the repairs are opposite — remove a
    flag versus add one — so a resolver collapsing them would hand half its readers a message
    fitting the other situation. That is the absent-versus-broken collapse this tree refuses.
    """
    bad = 0
    both = tenant_choice.resolve([_SANDBOX_FLAG, _LIVE_FLAG])
    if both.tenant != tenant_choice.BOTH:
        out.append(f"selftest: naming both tenants resolved to {both.tenant!r}, want both")
        bad += 1
    if both.named:
        out.append("selftest: an argv naming two tenants reported itself as named")
        bad += 1
    if both.tenant == tenant_choice.resolve([]).tenant:
        out.append("selftest: naming both and naming none collapsed into ONE answer")
        bad += 1
    if both.message() == tenant_choice.resolve([]).message():
        out.append("selftest: the two refusals share one message")
        bad += 1
    return bad


def a_repeated_flag_names_one_tenant(out: list[str]) -> int:
    """Check that the same flag twice is redundant, not contradictory.

    ⚑ `both` IS RESERVED FOR TWO DIFFERENT TENANTS, since that is the argv a caller genuinely
    cannot resolve. A resolver counting occurrences rather than distinct tenants would refuse a
    harmless repetition and send an operator hunting a conflict that is not there.
    """
    if tenant_choice.resolve([_SANDBOX_FLAG, _SANDBOX_FLAG]).tenant != tenant_choice.SANDBOX:
        out.append("selftest: a repeated flag was read as a conflict rather than one tenant")
        return 1
    return 0


def the_flag_is_read_anywhere_in_the_argv(out: list[str]) -> int:
    """Check that a tenant flag is found after a mode flag as well as before it.

    ⚑ THESE FLAGS TRAVEL BESIDE A MODE FLAG AND NO ORDER BETWEEN THEM IS MEANINGFUL. A resolver
    keyed on position answers correctly for the one spelling it was written against and silently
    for every other — the same shape as the dispatch under repair.
    """
    bad = 0
    for argv in ([_SANDBOX_FLAG, _MODE_FLAG], [_MODE_FLAG, _SANDBOX_FLAG]):
        if tenant_choice.resolve(argv).tenant != tenant_choice.SANDBOX:
            out.append(f"selftest: {argv!r} did not resolve to the sandbox")
            bad += 1
    return bad


def a_refusal_writes_its_reason_and_returns_a_code(out: list[str]) -> int:
    """Check that refusing writes the operator message and yields a non-zero exit code.

    ⚑ IT RETURNS THE CODE RATHER THAN EXITING, so this arm can drive it in-process. A refusal
    that exited from inside itself would be unreachable to a case that did not want a process
    boundary — which is what kept `store.tenant`'s decision untested.
    """
    bad = 0
    buf = io.StringIO()
    code = tenant_choice.refuse(tenant_choice.resolve([]), buf)
    if code != tenant_choice.REFUSAL_CODE:
        out.append(f"selftest: a refusal returned {code}, want {tenant_choice.REFUSAL_CODE}")
        bad += 1
    if not buf.getvalue().strip():
        out.append("selftest: a refusal wrote nothing — the operator is told nothing")
        bad += 1
    quiet = io.StringIO()
    if tenant_choice.refuse(tenant_choice.resolve([_LIVE_FLAG]), quiet) != 0:
        out.append("selftest: a NAMED tenant was refused")
        bad += 1
    if quiet.getvalue():
        out.append("selftest: a named tenant still produced a refusal message")
        bad += 1
    return bad


FAMILY = witness_family.of(
    key="tenant_choice",
    apex="an invocation's tenant is read from either flag wherever it appears, an unnamed or "
    "doubly-named tenant is refused with its own reason, and neither refusal quietly "
    "becomes the live store",
    subject="the choices `substrate.tenant_choice` resolves from an argv, offline",
    members=(
        witness_family.Member(
            name="the_two_tenant_flags_resolve_differently",
            claim="--sandbox and --live give different answers, and each gives the right one",
            cases=3,
        ),
        witness_family.Member(
            name="an_unstated_tenant_is_refused_not_defaulted",
            claim="naming no tenant refuses rather than quietly meaning the live store",
            cases=3,
        ),
        witness_family.Member(
            name="naming_both_tenants_is_its_own_refusal",
            claim="naming two tenants refuses, and refuses differently from naming none",
            cases=4,
        ),
        witness_family.Member(
            name="a_repeated_flag_names_one_tenant",
            claim="the same flag twice is redundant rather than contradictory",
        ),
        witness_family.Member(
            name="the_flag_is_read_anywhere_in_the_argv",
            claim="a tenant flag is found after a mode flag as well as before it",
            cases=2,
        ),
        witness_family.Member(
            name="a_refusal_writes_its_reason_and_returns_a_code",
            claim="refusing writes the operator message and yields a non-zero code, and a named "
            "tenant does neither",
            cases=4,
            premises=("an_unstated_tenant_is_refused_not_defaulted",),
        ),
    ),
)

_ARMS = (
    the_two_tenant_flags_resolve_differently,
    an_unstated_tenant_is_refused_not_defaulted,
    naming_both_tenants_is_its_own_refusal,
    a_repeated_flag_names_one_tenant,
    the_flag_is_read_anywhere_in_the_argv,
    a_refusal_writes_its_reason_and_returns_a_code,
)

_CASE_COUNT = FAMILY.count

_SELF_KEY = "substrate/tenant_choice_selftest.py"


def selftest() -> int:
    """Run every arm, report by typed record, and return an exit code."""
    out: list[str] = []
    failures = sum(arm(out) for arm in _ARMS)
    if failures:
        sys.stderr.write("\n".join(out) + "\n")
    return suite_emit.report(_SELF_KEY, _CASE_COUNT - failures, _CASE_COUNT)


if __name__ == "__main__":
    raise SystemExit(selftest() if "--selftest" in sys.argv or len(sys.argv) == 1 else 0)
