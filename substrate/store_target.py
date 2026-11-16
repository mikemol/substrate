#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Mike Mol
"""Report a postgres connection target for the tenant the invocation NAMED (drain-store).

⚑⚑⚑ THIS IS THE DISPATCH, AND THE DISPATCH IS THE DEFECT BEING REPAIRED. `jea/metalanguage/
store.py`'s `__main__` block recognises exactly two flags — its selftest one and its
credential-backend one — and lets every other argv fall through to a branch that unconditionally
opens the LIVE accessor. Measured: with that CLI, `--redacted-dsn --sandbox`, `--redacted-dsn
--live` and a bare invocation print BYTE-IDENTICAL output naming the live database. There is no
`--redacted-dsn` flag there and no `--sandbox` handling in that CLI at all — the flags are not
mishandled, they are unread.

⚑ AND THIS PARAGRAPH DELIBERATELY DOES NOT SPELL THAT SELFTEST FLAG. `suite_discovery` classifies
a file as a SUITE when it has an entry point and mentions the literal anywhere — docstrings
included, since a reader cannot tell prose from dispatch. Naming it here made the runner invoke
this CLI as a suite, which then correctly REFUSED for want of a tenant: a module describing a
defect became an instance of a different one. The discovery reader is doing what it documents;
the prose is what had to change.

⚑⚑ AND IT WAS FIRST DIAGNOSED AS *"the printer calls the wrong accessor"*, WHICH IS THE WRONG
REPAIR FOR THE RIGHT SYMPTOM. A printer reaching for the wrong accessor is a one-line
substitution and leaves the dispatch intact, so the NEXT flag added to that CLI is swallowed the
same way. What is wrong is not any line — it is that unknown argv reaches a live-store branch
instead of a refusal. That is why the repair is a module owning the DECISION and the REPORT
together, rather than an edit to a print statement.

⚑⚑⚑ AND IT COULD NOT LAND AS AN EDIT TO THAT FILE. The per-file gate is zero-tolerance and that
module carries hundreds of frozen findings, so ANY edit to it is refused and reverted — verified
here, not assumed. The gate's own guidance names this exact move: when the only consumer of an
extraction lives inside the frozen file, extracting one concern STRANDS, and the finish is to keep
cutting until the DISPATCH moves out too. This module is that cut. The monolith's CLI is not
repaired; it is SUPERSEDED, and the supersession is what makes the repair reachable.

⚑ THE THREE CONCERNS ARE THREE MODULES, AND THAT IS WHAT KEEPS EACH ONE CLEAN. `tenant_choice`
resolves the argv, `sandbox_target` and `live_target` assemble a target apiece, and this module
does nothing but route between them and print. A single module doing all three would be the shape
the monolith already is, one order of magnitude smaller — and the reason that shape cannot be
edited is the reason not to rebuild it.

⚑⚑ AN UNNAMED TENANT REFUSES RATHER THAN DEFAULTING, AND THAT IS THE HALF WITH TEETH. The
superseded CLI's bare invocation printed the live store; here it exits non-zero having named the
problem. Both directions have been measured on this tree — a live answer printed under a sandbox
question, and a sandbox count read as the live store's — so no default can be correct. Forgetting
to care must not be indistinguishable from choosing.

⚑ ONLY THE REDACTED FORM IS EVER PRINTED, AND THERE IS NO FLAG THAT PRINTS THE CREDENTIAL. A
reporter that was safe became a leak the moment the target gained a secret, silently, because the
invariant it relied on was never written down. The safe form is not the default here; it is the
whole surface.

⚑ NO CONNECTION IS OPENED. Everything this module reports is assembled, so it answers the same
way whether or not the store is up — which is exactly when an operator asks what target a tool
would use. A reporter that had to connect in order to say where it would connect could not answer
the question that gets asked during an outage.
"""

from __future__ import annotations

import sys

from substrate import live_target, sandbox_target, tenant_choice

#: The mode this CLI dispatches. ⚑ IT IS A DISPATCHED BRANCH, NOT A FLAG NOTHING READS — the
#: distinction the superseded CLI failed to make, where an unrecognised flag reached a live branch.
REDACTED_DSN = "--redacted-dsn"

#: The exit code an unrecognised argv returns. ⚑ AN UNKNOWN MODE REFUSES rather than falling
#: through to a default branch: falling through is the defect, and a permissive dispatch here
#: would reintroduce it under a new name.
USAGE_CODE = 2

_USAGE = (
    "usage: python3 -m substrate.store_target --redacted-dsn (--sandbox | --live)\n"
    "  the tenant is MANDATORY: there is no default, because forgetting to name one\n"
    "  would be indistinguishable from choosing one."
)


def assemble(tenant: str) -> sandbox_target.Target:
    """Assemble the named tenant's target, routing to the module that owns it.

    ⚑ IT TAKES A RESOLVED TENANT, NEVER AN ARGV. The decision and the routing are separate so
    that each is checkable alone: `tenant_choice` is driven with argvs and no targets, this is
    driven with tenants and no flags. A function taking argv would fold the two back together and
    reproduce the monolith's shape at a smaller scale.

    ⚑ AN UNROUTABLE TENANT RAISES RATHER THAN PICKING ONE. Reaching here with anything but a
    named tenant means the resolver and the router disagree, and guessing would turn a coding
    fault into a wrong-store read — the failure mode with no symptom.
    """
    if tenant == tenant_choice.SANDBOX:
        return sandbox_target.target()
    if tenant == tenant_choice.LIVE:
        return live_target.target()
    msg = f"unroutable tenant {tenant!r} — the resolver and the router disagree"
    raise ValueError(msg)


def render(tenant: str, target: sandbox_target.Target) -> str:
    """Render the report: the tenant NAMED, then its redacted target.

    ⚑⚑ IT NAMES THE TENANT BESIDE THE TARGET, WHICH IS THE HALF THE PREDECESSOR GOT WRONG. That
    reporter printed a target with no tenant line while accepting a tenant flag it ignored, so a
    reader who did not already know the answer read a confident wrong one. A footer that can
    disagree with its own subject is worse than one that is simply absent.

    ⚑ THE TENANT LINE IS DERIVED FROM THE SAME VALUE THAT SELECTED THE TARGET, never re-read from
    the argv. Two independent readings of "which tenant" is precisely how a label comes to
    disagree with the rows above it.
    """
    return f"tenant : {tenant}\ntarget : {target.redacted()}\n"


def main(argv: list[str]) -> int:
    """Dispatch on the mode, resolve the tenant, and report — refusing anything unstated.

    ⚑⚑ EVERY ARGV REACHES A DECISION AND NONE FALLS THROUGH. The mode is checked, the tenant is
    resolved, and an argv satisfying neither gets usage and a non-zero code. The superseded
    dispatch's defect was the absent `else`; making it present is the repair.
    """
    if REDACTED_DSN not in argv:
        sys.stderr.write(_USAGE + "\n")
        return USAGE_CODE
    choice = tenant_choice.resolve(argv)
    refusal = tenant_choice.refuse(choice)
    if refusal:
        return refusal
    sys.stdout.write(render(choice.tenant, assemble(choice.tenant)))
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
