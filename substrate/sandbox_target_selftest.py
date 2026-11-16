#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Mike Mol
"""The cases for `substrate.sandbox_target`: the target carries a port and a credential.

⚑⚑⚑ THE FIRST ARM IS THE DEFECT THIS MODULE WAS WRITTEN FOR, PINNED AS A CASE. The connector it
replaces named host, database and role and supplied NO port, so it fell through to the driver's
default — which was correct until the store moved to k8s and the host's own listener was retired.
Nothing failed at assembly time; the failure surfaced as `connection refused` at connect time, in
one tenant only, while the accessor beside it reported the right target the whole while. An arm
that asserts the port is PRESENT AND IS THE CONSUMER PORT is what makes that regression loud at
the layer where it is cheap.

⚑⚑ AND THE CASES DRIVE ASSEMBLY WITHOUT A DATABASE OR A KEYRING, WHICH IS WHY THEY CAN RUN AT
ALL. The predecessor interleaved target assembly, credential lookup and the connect call in one
function, so the only way to observe the target was to open a connection — and a suite that needs
a live server to read a transport is asserting the server. `target()` takes its credential source
as a parameter and returns a value, so both halves are checkable here, offline, in-process.

⚑ THE CREDENTIAL ARMS CHECK A DISTINCTION, NOT A VALUE. No case names a secret: they assert that
an ABSENT credential omits the key entirely while a PRESENT one puts it in, because a
present-but-empty password is an ATTEMPT to the driver and comes back as an authentication error —
which misreports "none was ever supplied" as "wrong credential". The two absences need different
repairs, so one message for both is the collapse under test.

⚑ THE REDACTION ARM ASSERTS SUBSTITUTION RATHER THAN DELETION, and checks that the secret is not
in the rendered mapping. A dropped key reads as "no credential is configured" — a different fact
an operator debugging an authentication failure would act on.
"""

from __future__ import annotations

import os
import sys
from contextlib import contextmanager
from typing import TYPE_CHECKING

from mikemol.witness import witness_family

from substrate import sandbox_target, store_endpoint, suite_emit

if TYPE_CHECKING:
    from collections.abc import Callable, Iterator

# A stand-in credential. ⚑ IT IS A FIXTURE, NOT A SECRET: the arms assert only whether the key is
# PRESENT, never what a real credential is, and nothing here reads the operator's keyring.
_FIXTURE = "fixture-not-a-credential"

# ⚑⚑ THE TRANSPORT FIXTURES, AND WHY THE OLD ONES WERE RETIRED (2026-09-22). These arms used to pin
# the NodePort `30432` and refuse `5432` as "the driver's default the predecessor fell through to".
# Both premises died with the cutover: the NodePort was retired, and `5432` is now the CORRECT port
# of luthen's ClusterIP Service. What survives is the rule: the target always carries an EXPLICIT
# port, from an override when one is set and from the owner's resolver otherwise — never a fall-
# through. The fixtures are deliberately unlike any real port, so no arm can pass by coincidence.
_OVERRIDE_HOST = "override.fixture"
_OVERRIDE_PORT = 45432
_RESOLVED_HOST = "resolved.fixture"
_RESOLVED_PORT = 46432

# The reset fixture: two tables and one view, and the statement count they must produce. ⚑ THE
# COUNT IS DERIVED FROM THE FIXTURE rather than typed, so the two cannot disagree.
_RELATIONS = (("t_one", "BASE TABLE"), ("v_one", "VIEW"), ("t_two", "BASE TABLE"))
_WANT_STATEMENTS = len(_RELATIONS)


@contextmanager
def _env(host: str | None, port: str | None) -> Iterator[None]:
    """Set (or unset) the transport override for the block, then restore it exactly."""
    saved = {v: os.environ.get(v) for v in (sandbox_target.HOST_VAR, sandbox_target.PORT_VAR)}
    for var, val in ((sandbox_target.HOST_VAR, host), (sandbox_target.PORT_VAR, port)):
        if val is None:
            os.environ.pop(var, None)
        else:
            os.environ[var] = val
    try:
        yield
    finally:
        for var, val in saved.items():
            if val is None:
                os.environ.pop(var, None)
            else:
                os.environ[var] = val


@contextmanager
def _resolver_answers(host: str, port: int) -> Iterator[None]:
    """Replace the owner's resolver with a fixed answer for the block — no subprocess, no cluster.

    ⚑ A suite that reached the real resolver would pass or fail with luthen's state, reporting the
    owner's change as this module's defect; the first run after the wiring did exactly that.
    """
    real = store_endpoint.resolve

    def fixed(
        runner: Callable[[list[str]], tuple[int, str]] = store_endpoint.run,
    ) -> store_endpoint.Endpoint:
        del runner  # the fixture answers without running anything
        return store_endpoint.Endpoint(host=host, port=port, as_of="fixture")

    store_endpoint.resolve = fixed
    try:
        yield
    finally:
        store_endpoint.resolve = real


def _target(secret: str | None) -> sandbox_target.Target:
    """Assemble a target with the given credential under the transport OVERRIDE, offline."""
    with _env(_OVERRIDE_HOST, str(_OVERRIDE_PORT)):
        return sandbox_target.target(lambda: secret)


def the_override_is_the_transport(out: list[str]) -> int:
    """Check that an explicit host/port override is the transport, carried as an explicit port.

    ⚑⚑ THE REGRESSION THIS MODULE WAS WRITTEN FOR IS A MISSING PORT, and that is still refused: a
    target with no port falls through to the driver's choice, which is a guess.
    """
    bad = 0
    kw = _target(_FIXTURE).keywords()
    if "port" not in kw:
        out.append("selftest: the assembled target carries NO port — the defect this replaces")
        bad += 1
    elif (kw["host"], kw["port"]) != (_OVERRIDE_HOST, _OVERRIDE_PORT):
        out.append(f"selftest: override ignored: {kw['host']}:{kw['port']}")
        bad += 1
    return bad


def the_resolver_answers_when_no_override(out: list[str]) -> int:
    """Check that with no override the transport is the owner's resolver's answer, not a default."""
    with _env(None, None), _resolver_answers(_RESOLVED_HOST, _RESOLVED_PORT):
        kw = sandbox_target.target(lambda: _FIXTURE).keywords()
    if (kw.get("host"), kw.get("port")) != (_RESOLVED_HOST, _RESOLVED_PORT):
        out.append(
            f"selftest: no override, but transport is {kw.get('host')}:{kw.get('port')}, "
            "not the resolver's answer"
        )
        return 1
    return 0


def an_absent_credential_omits_the_key(out: list[str]) -> int:
    """Check that no credential means no `password` key, rather than an empty one.

    ⚑ AN EMPTY PASSWORD IS AN ATTEMPT. Supplying one turns "no credential was ever placed" into an
    authentication failure, and the two need different repairs.
    """
    if "password" in _target(None).keywords():
        out.append("selftest: an absent credential still emitted a password key")
        return 1
    return 0


def a_present_credential_rides_along(out: list[str]) -> int:
    """Check that a credential supplied by the source reaches the keyword mapping.

    ⚑ THE OTHER HALF OF THE OMISSION ARM. Checking only that absence omits would pass on a module
    that never emitted a credential at all — which is the predecessor's behaviour exactly.
    """
    if _target(_FIXTURE).keywords().get("password") != _FIXTURE:
        out.append("selftest: a supplied credential did not reach the keyword mapping")
        return 1
    return 0


def the_tenant_is_the_sandbox_not_the_live_store(out: list[str]) -> int:
    """Check that the database and the role are both the sandbox's, and agree.

    ⚑⚑ THE WRONG-TENANT HAZARD, AT ASSEMBLY. A target naming the live database, or naming the
    sandbox database with the live role, would let a probe that exists to be harmed reach the store
    that does not. Both fields are checked, and that they match: the split rests on the credential,
    so the role is the half that carries it.
    """
    bad = 0
    kw = _target(_FIXTURE).keywords()
    if kw["dbname"] != sandbox_target.DB_DEFAULT:
        out.append(f"selftest: dbname is {kw['dbname']!r}, want the sandbox database")
        bad += 1
    if kw["user"] != kw["dbname"]:
        out.append(f"selftest: role {kw['user']!r} does not match database {kw['dbname']!r}")
        bad += 1
    return bad


def the_redaction_substitutes_and_does_not_drop(out: list[str]) -> int:
    """Check that a printable target keeps the key, hides the value, and leaks nothing.

    ⚑ SUBSTITUTION, NOT DELETION. A dropped key reads as "no credential is configured", which is a
    different fact; and the arm also asserts the real value is absent, since a reporter that was
    safe became a leak once the target gained a secret.
    """
    bad = 0
    red = _target(_FIXTURE).redacted()
    if "password" not in red:
        out.append("selftest: redaction DROPPED the password key instead of substituting")
        bad += 1
    if red.get("password") == _FIXTURE:
        out.append("selftest: the redacted target still carries the credential")
        bad += 1
    if red.get("port") != _OVERRIDE_PORT:
        out.append("selftest: redaction altered the transport")
        bad += 1
    return bad


def a_reset_drops_views_before_tables(out: list[str]) -> int:
    """Check the reset ordering: every view is dropped before any table.

    ⚑ A VIEW DEPENDS ON THE TABLES IT SELECTS FROM, so tables-first fails on the dependency and
    leaves a PARTIAL reset — worse than none, since it leaves exactly the ambiguity a reset exists
    to remove.
    """
    bad = 0
    stmts = sandbox_target.reset_statements(list(_RELATIONS))
    kinds = ["VIEW" if s.startswith("DROP VIEW") else "TABLE" for s in stmts]
    if len(stmts) != _WANT_STATEMENTS:
        out.append(f"selftest: {len(stmts)} statements for {_WANT_STATEMENTS} relations")
        bad += 1
    if "TABLE" in kinds and "VIEW" in kinds and kinds.index("VIEW") > kinds.index("TABLE"):
        out.append("selftest: a table is dropped before a view — the dependency order is wrong")
        bad += 1
    if not all("CASCADE" in s for s in stmts):
        out.append("selftest: a drop statement is missing CASCADE")
        bad += 1
    return bad


FAMILY = witness_family.of(
    key="sandbox_target",
    apex="the sandbox tenant's connection target is assembled with its transport and its "
    "credential complete, names the sandbox rather than the live store, prints without "
    "leaking, and orders a reset by dependency",
    subject="the targets `substrate.sandbox_target` assembles, offline",
    members=(
        witness_family.Member(
            name="the_override_is_the_transport",
            claim="an explicit host/port override is the transport, carried as an explicit port",
            cases=2,
        ),
        witness_family.Member(
            name="the_resolver_answers_when_no_override",
            claim="with no override, the transport is the owner's resolver's answer",
        ),
        witness_family.Member(
            name="an_absent_credential_omits_the_key",
            claim="no credential means no password key, rather than an empty one",
        ),
        witness_family.Member(
            name="a_present_credential_rides_along",
            claim="a credential from the source reaches the keyword mapping",
        ),
        witness_family.Member(
            name="the_tenant_is_the_sandbox_not_the_live_store",
            claim="the database and the role are both the sandbox's, and they agree",
            cases=2,
        ),
        witness_family.Member(
            name="the_redaction_substitutes_and_does_not_drop",
            claim="a printable target keeps the key, hides the value, and leaks nothing",
            cases=3,
            premises=("a_present_credential_rides_along",),
        ),
        witness_family.Member(
            name="a_reset_drops_views_before_tables",
            claim="every view is dropped before any table, with CASCADE throughout",
            cases=3,
        ),
    ),
)

_ARMS = (
    the_override_is_the_transport,
    the_resolver_answers_when_no_override,
    an_absent_credential_omits_the_key,
    a_present_credential_rides_along,
    the_tenant_is_the_sandbox_not_the_live_store,
    the_redaction_substitutes_and_does_not_drop,
    a_reset_drops_views_before_tables,
)

_CASE_COUNT = FAMILY.count

_SELF_KEY = "substrate/sandbox_target_selftest.py"


def selftest() -> int:
    """Run every arm, report by typed record, and return an exit code."""
    out: list[str] = []
    failures = sum(arm(out) for arm in _ARMS)
    if failures:
        sys.stderr.write("\n".join(out) + "\n")
    return suite_emit.report(_SELF_KEY, _CASE_COUNT - failures, _CASE_COUNT)


if __name__ == "__main__":
    raise SystemExit(selftest() if "--selftest" in sys.argv or len(sys.argv) == 1 else 0)
