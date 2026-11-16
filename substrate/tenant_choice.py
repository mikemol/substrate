#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Mike Mol
"""Resolve which tenant an invocation NAMES, and refuse when it named none (drain-store).

⚑⚑⚑ THIS IS A DEFECT IN THE DISPATCH, NOT IN A PRINTER, AND THE TWO NEED DIFFERENT REPAIRS.
`jea/metalanguage/store.py`'s `__main__` block dispatches `--selftest` and `--credential-backend`
and lets EVERYTHING ELSE fall through to a branch that unconditionally opens the LIVE accessor.
So `--redacted-dsn --sandbox`, `--redacted-dsn --live` and a bare invocation print BYTE-IDENTICAL
output — `dbname: substrate`, the live store, under every question. There is no `--redacted-dsn`
flag there and no `--sandbox` handling in that CLI at all.

⚑⚑ IT WAS FIRST REPORTED AS *"the printer calls the wrong accessor"* AND THAT READING IS WRONG.
A printer reaching for the wrong accessor is a one-line substitution: point it at the other one.
A dispatch that IGNORES EVERY FLAG IT DOES NOT RECOGNISE is a different fault with a different
blast radius — every future flag added to that CLI inherits the silence, and the wrongness is not
in any line you could point at. Repairing the printer would have left the dispatch intact and the
next flag would have been swallowed the same way. The dispatch is the thing being fixed, which is
why the repair is a module holding the DECISION rather than an edit to a print statement.

⚑⚑⚑ AND THAT IS WHY AN EXTRACTION ALONE WOULD HAVE STRANDED. The per-file gate's own guidance for
a frozen monolith is to extract the concern into a new clean module and let consumers import it —
but wiring a new module in is itself an edit to the frozen file, so a lone extraction leaves a
module with no consumer. What makes this one land is that the decision it holds is the one the
CLI must consult: it is not a helper the file could keep ignoring.

⚑ THE DECISION IS PURE, TOTAL, AND SEPARATE FROM ANY CONNECTION, which is the split
`store._tenant_named` already drew and this module preserves rather than reinvents. That function
is documented as *"split out so the contract is testable without a store"* — assembling the answer
needs no postgres, no keyring and no driver, so every case here runs offline. A resolver that
opened a connection to say which tenant you meant would be asserting the store's availability
instead of the rule.

⚑⚑ FOUR OUTCOMES, AND THE TWO REFUSALS ARE NOT ONE. `unstated` and `both` are separate answers
because they are separate operator mistakes with separate repairs — "you forgot to say" versus
"you said two things" — and a resolver collapsing them into a single `error` would hand the
reader a message that fits one of the two situations. That is the same absent-versus-broken
collapse `sandbox_target` refuses one layer down, applied to an argv.

⚑⚑ AND `unstated` REFUSES RATHER THAN DEFAULTING, WHICH IS THE WHOLE POINT. `store.tenant`'s own
note records the ruling (operator, 2026-08-18): three failure modes, and the third is the one a
default GUARANTEES — *"forgetting to care is indistinguishable from choosing"*. Both spellings
exist precisely so that neither is a default; a resolver that filled one in would restore the
silent branch the flags were added to remove. There is no default tenant here and no environment
variable that supplies one.

⚑ IT IMPORTS NOTHING FROM `jea/`, AND THAT IS LOAD-BEARING RATHER THAN TIDY. A module extracted
out of that package but still NAMING it inherits the untyped hub through the import and cannot be
made clean under this tree's per-file gate — measured on the sibling extractions, which succeeded
precisely because they reached back for nothing. The flag spellings are therefore re-stated here
as this module's own authority rather than imported, and the cases pin them against the consumer
that must agree.
"""

from __future__ import annotations

import sys
from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from typing import TextIO

#: The tenant a `--sandbox` argv names.
SANDBOX = "sandbox"
#: The tenant a `--live` argv names.
LIVE = "live"
#: No tenant flag appeared. ⚑ A REFUSAL, never a synonym for `live`.
UNSTATED = "unstated"
#: Both tenant flags appeared. ⚑ A REFUSAL, and NOT the same one as `UNSTATED`.
BOTH = "both"

#: The flag that names each tenant. ⚑ BOTH SPELLINGS EXIST SO THAT NEITHER IS A DEFAULT: `--live`
#: is the half that was missing, and its absence is exactly what made "no flag" MEAN live silently.
FLAGS = {"--sandbox": SANDBOX, "--live": LIVE}

#: How many distinct tenants an argv may name. ⚑ NAMED RATHER THAN SPELLED AT THE COMPARISON: the
#: rule is "exactly one", and a bare literal states the arithmetic while hiding the rule.
_ONE_TENANT = 1

#: The exit code a refused invocation returns — the same one `store.tenant` already exits with, so
#: a caller migrating from that path sees no change in what a wrong argv costs.
REFUSAL_CODE = 2


@dataclass(frozen=True, slots=True)
class Choice:
    """One argv's tenant answer: which tenant, whether it is usable, and why not.

    ⚑ THE REFUSAL CARRIES ITS REASON AS DATA RATHER THAN AS A RAISED MESSAGE. A caller deciding
    what to print, and a case asserting which refusal fired, need the same fact; an exception
    gives the first a string to re-parse and the second a message to match on. `tenant` is the
    discriminator — `unstated` and `both` stay two answers all the way to the operator.
    """

    tenant: str

    @property
    def named(self) -> bool:
        """Report whether this argv actually named exactly one tenant."""
        return self.tenant in (SANDBOX, LIVE)

    def message(self) -> str:
        """Render the operator-facing refusal, or the empty string when there is nothing to refuse.

        ⚑ THE TWO REFUSALS SAY DIFFERENT THINGS BECAUSE THE REPAIRS DIFFER: add a flag, versus
        remove one. A shared message would send half its readers to the wrong edit.
        """
        if self.tenant == UNSTATED:
            return (
                "tenant: no tenant named — pass --sandbox or --live.\n"
                "  no default tenant exists: forgetting to care would be\n"
                "  indistinguishable from choosing, and both directions have been\n"
                "  measured (a live answer printed under a sandbox question, and a\n"
                "  sandbox count read as the live store's)."
            )
        if self.tenant == BOTH:
            return (
                "tenant: --sandbox and --live were BOTH named — pass exactly one.\n"
                "  this is not the same fault as naming neither, and it is not\n"
                "  resolved by picking one for you: an invocation that states two\n"
                "  tenants has not decided which store it meant."
            )
        return ""


def resolve(argv: list[str]) -> Choice:
    """Resolve the tenant this argv names — pure, total, and needing no store.

    ⚑ IT READS THE WHOLE ARGV RATHER THAN A LEADING POSITION, because these flags travel beside
    a mode flag and no order between them is meaningful. A resolver keyed on position would
    answer correctly for the spelling it was written against and silently for every other.

    ⚑ A REPEATED FLAG IS NOT `both`. `--sandbox --sandbox` names one tenant twice, which is
    redundant rather than contradictory; `both` is reserved for an argv that names two DIFFERENT
    tenants, since that is the one a caller cannot resolve.
    """
    named = {FLAGS[a] for a in argv if a in FLAGS}
    if not named:
        return Choice(UNSTATED)
    if len(named) > _ONE_TENANT:
        return Choice(BOTH)
    return Choice(named.pop())


def refuse(choice: Choice, stream: TextIO | None = None) -> int:
    """Write the refusal for an unusable choice and return its exit code, or 0 when it is usable.

    ⚑ IT RETURNS THE CODE RATHER THAN EXITING, so a caller composes it into its own dispatch and
    a case can drive it without a subprocess. `store.tenant` exits from inside itself, which is
    what made its decision unreachable to a case that did not want a process boundary.
    """
    if choice.named:
        return 0
    out = stream if stream is not None else sys.stderr
    out.write(choice.message() + "\n")
    return REFUSAL_CODE
