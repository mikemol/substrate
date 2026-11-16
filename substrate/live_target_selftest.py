#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Mike Mol
"""The cases for `substrate.live_target`: the live tenant, sharing transport, differing in identity.

⚑⚑⚑ THE LOAD-BEARING ARM IS THAT THE TWO TENANTS SHARE A TRANSPORT AND DIFFER IN IDENTITY. That
is the exact partition the drift violated: a connector named host, database and role while
supplying no port, so one tenant followed the NodePort cutover and the other silently kept the
driver's default. An arm asserting the live target's port EQUALS the sandbox's is what makes a
future divergence loud — and it is stronger than pinning a number, because it fails whichever of
the two moves alone.

⚑⚑ AND THE IDENTITY ARM IS ITS COMPLEMENT, WITHOUT WHICH THE FIRST WOULD BE SATISFIED BY A COPY.
A module returning the sandbox's target verbatim would pass every transport check while
reproducing the wrong-tenant read this whole arc exists to prevent. So the database and the role
are asserted to DIFFER from the sandbox's, and to be the live ones.

⚑ THE CASES DRIVE ASSEMBLY WITH NO DATABASE AND NO KEYRING, which is the property both target
modules were split out to have. The credential source is a parameter and assembly returns a
value, so a transport can be read without a server — a suite needing a live store to check a
target would be asserting the store.

⚑ NO CASE NAMES A SECRET. The credential arms assert a DISTINCTION — that an absent credential
omits the key while a present one supplies it — because a present-but-empty password is an
ATTEMPT to the driver and comes back as an authentication error, misreporting "none was ever
supplied" as "wrong credential".
"""

from __future__ import annotations

import os
import sys

from mikemol.witness import witness_family

from substrate import live_target, sandbox_target, suite_emit

# A stand-in credential. ⚑ A FIXTURE, NOT A SECRET: the arms assert only whether the key is
# present, never what a real credential is, and nothing here reads the operator's keyring.
_FIXTURE = "fixture-not-a-credential"

# ⚑⚑ AN EXPLICIT TRANSPORT OVERRIDE, SO NO ARM REACHES THE OWNER'S RESOLVER (2026-09-22). This
# suite used to refuse port `5432` as the driver default the predecessor fell through to; since
# the cutover `5432` is luthen's CORRECT ClusterIP port, and assembling without an override now
# asks luthen's resolver — which made the first post-wiring run depend on luthen's state. The
# fixture port is deliberately unlike any real one.
_OVERRIDE_HOST = "override.fixture"
_OVERRIDE_PORT = 45432


def _assemble(build: object, secret: str | None) -> sandbox_target.Target:
    """Assemble a target under the transport override, restoring the environment exactly."""
    saved = {v: os.environ.get(v) for v in (sandbox_target.HOST_VAR, sandbox_target.PORT_VAR)}
    os.environ[sandbox_target.HOST_VAR] = _OVERRIDE_HOST
    os.environ[sandbox_target.PORT_VAR] = str(_OVERRIDE_PORT)
    try:
        if build is live_target.target:
            return live_target.target(lambda: secret)
        return sandbox_target.target(lambda: secret)
    finally:
        for var, val in saved.items():
            if val is None:
                os.environ.pop(var, None)
            else:
                os.environ[var] = val


def _live(secret: str | None) -> sandbox_target.Target:
    """Assemble a live target with the given credential, offline."""
    return _assemble(live_target.target, secret)


def _sandbox(secret: str | None) -> sandbox_target.Target:
    """Assemble a sandbox target with the given credential, offline."""
    return _assemble(sandbox_target.target, secret)


def the_transport_is_shared_with_the_sandbox(out: list[str]) -> int:
    """Check that host and port match the sandbox's, rather than being restated.

    ⚑⚑ THIS IS THE DRIFT, INVERTED INTO A CASE. Host and port are properties of the STORE, not of
    a tenant; the measured defect was one tenant following a cutover while the other did not.
    Asserting EQUALITY between the two targets fails whichever side moves alone, which pinning a
    literal would not.
    """
    bad = 0
    live = _live(_FIXTURE).keywords()
    sand = _sandbox(_FIXTURE).keywords()
    if live["host"] != sand["host"]:
        out.append(f"selftest: hosts diverged — live {live['host']!r}, sandbox {sand['host']!r}")
        bad += 1
    if live["port"] != sand["port"]:
        out.append(f"selftest: ports diverged — live {live['port']!r}, sandbox {sand['port']!r}")
        bad += 1
    if (live["host"], live["port"]) != (_OVERRIDE_HOST, _OVERRIDE_PORT):
        out.append(
            f"selftest: the live target ignored the transport override: "
            f"{live['host']}:{live['port']}"
        )
        bad += 1
    return bad


def the_identity_differs_from_the_sandbox(out: list[str]) -> int:
    """Check that the database and the role are the live ones, not the sandbox's.

    ⚑⚑ WITHOUT THIS THE TRANSPORT ARM WOULD PASS ON A VERBATIM COPY. A module returning the
    sandbox's target would share its transport perfectly and hand every live query to the store
    that exists to be harmed — the wrong-tenant read, arriving through the module built to
    prevent it.
    """
    bad = 0
    live = _live(_FIXTURE).keywords()
    sand = _sandbox(_FIXTURE).keywords()
    if live["dbname"] == sand["dbname"]:
        out.append("selftest: the live target names the SANDBOX database")
        bad += 1
    if live["user"] == sand["user"]:
        out.append("selftest: the live target authenticates as the SANDBOX role")
        bad += 1
    if live["dbname"] != live_target.DB_DEFAULT:
        out.append(f"selftest: dbname is {live['dbname']!r}, want the live database")
        bad += 1
    if live["user"] != live_target.USER_DEFAULT:
        out.append(f"selftest: role is {live['user']!r}, want the live role")
        bad += 1
    return bad


def a_credential_distinction_is_preserved(out: list[str]) -> int:
    """Check that an absent credential omits the key while a present one supplies it.

    ⚑ AN EMPTY PASSWORD IS AN ATTEMPT. Supplying one turns "no credential was ever placed" into
    an authentication failure, and the two need different repairs. Both halves are asserted:
    checking only the omission would pass on a module that never emitted a credential at all.
    """
    bad = 0
    if "password" in _live(None).keywords():
        out.append("selftest: an absent credential still emitted a password key")
        bad += 1
    if _live(_FIXTURE).keywords().get("password") != _FIXTURE:
        out.append("selftest: a supplied credential did not reach the keyword mapping")
        bad += 1
    return bad


def the_redaction_substitutes_and_does_not_leak(out: list[str]) -> int:
    """Check that a printable live target keeps the key, hides the value, and leaks nothing.

    ⚑ SUBSTITUTION, NOT DELETION. A dropped key reads as "no credential is configured" — a
    different fact an operator debugging an authentication failure would act on. The arm also
    asserts the real value is absent, since a reporter that was safe became a leak once the
    target gained a secret.
    """
    bad = 0
    red = _live(_FIXTURE).redacted()
    if "password" not in red:
        out.append("selftest: redaction DROPPED the password key instead of substituting")
        bad += 1
    if red.get("password") == _FIXTURE:
        out.append("selftest: the redacted live target still carries the credential")
        bad += 1
    return bad


FAMILY = witness_family.of(
    key="live_target",
    apex="the live tenant's target shares the store's transport with the sandbox, differs from "
    "it in database and role, keeps the absent-versus-present credential distinction, and "
    "prints without leaking",
    subject="the targets `substrate.live_target` assembles, offline",
    members=(
        witness_family.Member(
            name="the_transport_is_shared_with_the_sandbox",
            claim="host and port equal the sandbox's, and both follow an explicit override",
            cases=3,
        ),
        witness_family.Member(
            name="the_identity_differs_from_the_sandbox",
            claim="the database and the role are the live ones, not the sandbox's",
            cases=4,
        ),
        witness_family.Member(
            name="a_credential_distinction_is_preserved",
            claim="an absent credential omits the key while a present one supplies it",
            cases=2,
        ),
        witness_family.Member(
            name="the_redaction_substitutes_and_does_not_leak",
            claim="a printable target keeps the key, hides the value, and leaks nothing",
            cases=2,
            premises=("a_credential_distinction_is_preserved",),
        ),
    ),
)

_ARMS = (
    the_transport_is_shared_with_the_sandbox,
    the_identity_differs_from_the_sandbox,
    a_credential_distinction_is_preserved,
    the_redaction_substitutes_and_does_not_leak,
)

_CASE_COUNT = FAMILY.count

_SELF_KEY = "substrate/live_target_selftest.py"


def selftest() -> int:
    """Run every arm, report by typed record, and return an exit code."""
    out: list[str] = []
    failures = sum(arm(out) for arm in _ARMS)
    if failures:
        sys.stderr.write("\n".join(out) + "\n")
    return suite_emit.report(_SELF_KEY, _CASE_COUNT - failures, _CASE_COUNT)


if __name__ == "__main__":
    raise SystemExit(selftest() if "--selftest" in sys.argv or len(sys.argv) == 1 else 0)
