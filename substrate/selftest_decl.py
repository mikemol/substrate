#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Mike Mol
"""One tool's `--selftest` DECLARATION, and the static refusal it makes possible.

⚑⚑⚑ WHY THIS IS PROMOTED (gate-G80). `scripts/climode.py` carries nine definitions and
`substrate/climode.py` carries three — `Mode`, `split_flag`, `from_pairs` were promoted and
`Selftest`, `selftest_rows`, `self_including`, `branch_bounds`, `contract_rows` were not. That
half-finished promotion is what blocks the bare-import paydown: `procstruct` imports
`Selftest, contract_rows` and `check_mode_contracts` imports the module whole, so repointing
either at the package would fail on a name it does not export. **The order is forced** —
promote, then repoint.

⚑⚑ THE MODEL IS THE ONE `Mode` ALREADY SETTLED AND IS DELIBERATELY NOT A FORK. `Arm` from
gcalculus' `farm.py` → `Mode` → this, with the load-bearing property carried through unchanged:
**every declared field is one a discriminator can CHECK**, so a declaration that stops being
true is detectable rather than merely stale.

⚑⚑⚑ `none` IS A STATE, NOT AN ABSENT KEY, AND THAT IS THE WHOLE POINT OF THE RECORD. An absent
declaration and a declared `none` look identical to a `dict.get`, which is exactly the collapse
this breaks: a tool with no record is UNDECLARED (nobody has looked); a tool declaring `none`
has been looked at and found to need no suite. Those want different next actions, and one
silence cannot carry both. It converts an absence that reads as an oversight into a claim a
gate can hold to a reason.

⚑⚑ `runs_roster` IS THE FIELD THE FORK BOMB NEEDED AND NOBODY COULD WRITE. A suite that itself
invokes the roster is a legitimate thing to want — a gate wanting to know the selftests pass —
and it is ALSO the edge that closes the cycle. With membership decided by convention there was
nowhere to say so, and the measured cost was six generations, load 54.93, 68 concurrent
selftest processes on a ten-core box. Declared, it becomes a STATIC refusal.

⚑ AND THE STATIC REFUSAL CANNOT REPLACE THE RUNTIME ONE, WHICH IS WHY BOTH SHIP. A declaration
governs only the tools that made one; an undeclared tool, or one whose suite grows a roster
call tomorrow, is invisible here and caught only by the ppid walk. Naming this "the fix" would
be the census-green error — a fact about the declared population reported as a fact about the
process tree.

⚑ THIS DECLARES, IT DOES NOT DISPATCH. Discovery and invocation stay with the runner; what is
shared is the SHAPE of the claim, so a discriminator can be written once instead of per tool.
"""

from __future__ import annotations

from dataclasses import dataclass

# ⚑ A CLOSED SET, REFUSED AT CONSTRUCTION. See `__post_init__`.
STATES: tuple[str, ...] = ("suite", "fixture", "none")


@dataclass(frozen=True, slots=True)
class Selftest:
    """A tool's declared selftest posture, with every field a discriminator can check.

    `state`        one of `STATES`. `suite` produces a verdict record; `fixture` dispatches
                   and is MEANT to fail (a positive control for the runner itself); `none`
                   declares that this tool has no selftest.
    `why`          for `none`, WHY there is none — the field that makes the state a claim
                   rather than a shrug. Required for `none`, checked by `contract`.
    `key`          the record key a `suite` reports under, when it differs from the tool's
                   own path (a decomposed tool reports under its parent).
    `requires`     packages the suite declares it needs, so the runner can supply them.
    `tenant`       which store tenant the suite must resolve, or None.
    `runs_roster`  whether this suite itself invokes the roster that contains it.
    """

    state: str = "suite"
    why: str = ""
    key: str | None = None
    requires: tuple[str, ...] = ()
    tenant: str | None = None
    runs_roster: bool = False

    def __post_init__(self) -> None:
        """Refuse an unrecognised state rather than normalising it to a default.

        ⚑ A TYPO'D STATE SILENTLY BECOMING `suite` WOULD PUT A TOOL WITH NO SUITE IN THE
        ROSTER, and the runner would then report it SILENT — a defect manufactured by the
        declaration built to prevent one.
        """
        if self.state not in STATES:
            msg = (
                f"Selftest(state={self.state!r}) — not one of {STATES}. A state is a "
                "closed set: an unrecognised value must refuse, never default."
            )
            raise ValueError(msg)

    @property
    def runnable(self) -> bool:
        """Whether the runner should INVOKE this tool. DERIVED from `state`, never stored.

        ⚑ THE BOOLEAN IS A PROJECTION OF THE STATE. Storing both would be two spellings of
        one fact that can disagree — the one-spelling defect this corpus has already paid for
        twice, inside the readers written to find spelling disagreements.
        """
        return self.state == "suite"

    def contract(self) -> tuple[bool, str]:
        """Return `(ok, why)` — hold THIS declaration to its own fields.

        ⚑ A DECLARATION NOBODY CHECKS IS A COMMENT WITH A CONSTRUCTOR AROUND IT. These are
        checked against each other, because the disagreements they admit are internal: a
        `none` with no reason is the shrug the record exists to replace, and a runner
        instruction on a tool the runner never invokes is configuration for a call that never
        happens.
        """
        if self.state == "none" and not self.why.strip():
            return False, (
                "declares state='none' with no `why` — an undeclared absence with "
                "a constructor around it. Name the reason this tool needs no "
                "suite, or declare the state it actually has."
            )
        # ⚑ A `key` ON A NON-SUITE IS A PROMISE NOTHING KEEPS — it names a report nobody
        #   writes, which is the built-then-orphaned shape in declaration form.
        if self.key and self.state != "suite":
            return False, (
                f"declares a record `key` but state={self.state!r} — only a "
                "`suite` emits a record, so this key names a report nobody writes"
            )
        for name, value in (("requires", self.requires), ("tenant", self.tenant)):
            if value and self.state != "suite":
                return False, (
                    f"declares `{name}` but state={self.state!r} — that field "
                    "instructs the runner how to INVOKE a suite, and this tool is "
                    "never invoked"
                )
        # ⚑⚑ AND THIS ONE MATTERS MOST: a tool the runner never invokes cannot close a cycle,
        #   so the edge has no referent — and the static reader would then name a tool no
        #   roster runs, a FALSE FINDING out of the reader built to prevent the fork bomb.
        if self.runs_roster and self.state != "suite":
            return False, (
                f"declares runs_roster but state={self.state!r} — only an invoked "
                "suite can close the roster cycle, so this edge has no referent"
            )
        return True, ""


@dataclass(frozen=True, slots=True)
class Cycle:
    """What the static roster-cycle read found, and what it could not see.

    ⚑ THE BOUND TRAVELS WITH THE VERDICT (⟡bounds-in-band). An empty `closing` printed bare
    reads as *no tool closes the cycle*, which is a stronger claim than the read can carry —
    it saw only the tools that made a declaration.
    """

    closing: tuple[str, ...] = ()
    declared: int = 0

    @property
    def bound(self) -> str:
        """State what this read did NOT cover, in band with its result."""
        return (
            f"read {self.declared} DECLARED tool(s) — an undeclared tool, or one whose "
            "suite grows a roster call later, is invisible here and is caught only by "
            "the runtime ppid walk"
        )


def self_including(declared: dict[str, Selftest], roster_marker: str) -> Cycle:
    """Return the tools whose declaration says their suite RUNS THE ROSTER.

    ⚑ THE ROSTER TOOL ITSELF IS EXCLUDED BY NAME, not by a flag on the record. Keeping the
    exemption in the READER means a caller passing a different roster gets a different
    exemption, instead of minting a field a second tool could set to exempt itself.

    ⚑⚑ AND THE RESULT CARRIES ITS DENOMINATOR, because an empty list over an empty
    declaration set and an empty list over the whole fleet are different facts.
    """
    closing = tuple(
        sorted(
            tool for tool, decl in declared.items() if decl.runs_roster and tool != roster_marker
        )
    )
    return Cycle(closing=closing, declared=len(declared))


def failing(declared: dict[str, Selftest]) -> tuple[tuple[str, str], ...]:
    """Return `(tool, why)` for every declaration that contradicts itself."""
    return tuple(
        (tool, why) for tool, decl in declared.items() for ok, why in (decl.contract(),) if not ok
    )
