#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Mike Mol
"""RUN a decline's guarding check — because a refusal nobody verifies is a comment.

⚑⚑⚑ THE CHECK IS RUN, NOT QUOTED. A `Decline` naming a command nobody executes is the inert-guard
shape this repo has recorded five times — present, greppable, and doing nothing. The whole value
of the record type is that a refusal becomes FALSIFIABLE, and a listing that never executes
anything makes GUARDED and UNGUARDED indistinguishable.

⚑⚑ FOUR VERDICTS, AND THE DISTINCTIONS ARE THE DESIGN:

    GUARDED    the check ran and passed — the refusal still holds
    LAPSED     the check RAN AND FAILED — ⚑ the rejected reading may now be true, OR the check has
               drifted off its subject. Either way the record stopped being load-bearing and
               someone must look. It does NOT mean the rejected reading is now correct.
    UNCHECKED  the check could not run at all — ⚑ a fact about THIS MACHINE, never evidence either
               way about the refusal. Collapsing it into LAPSED reports an environment as a claim.
    UNGUARDED  no check declared — a comment with a record around it, REPORTED rather than hidden,
               because an unguarded decline is the *absent argument reads as an absent objection*
               defect wearing this record type's own clothes.

⚑ THE TIMEOUT IS THE DECLINE'S OWN, SEPARATE FROM ANY OTHER BUDGET. A decline's check is a real
gate and several are corpus walks. MEASURED: one exceeded a 180s budget and reported UNCHECKED —
correct behaviour, and the cause was the host running in POWERSAVE. ⚑ A timeout tuned on a fast
machine turns a slow one into a tree full of unverifiable refusals, which is a fact about the box
read as a fact about the claims.

⚑ IDENTICAL CHECKS RUN ONCE. Two declines can share a discriminator because they are different
REFUSALS guarded by the same command — legitimate, and not a duplicate record. The memo is keyed
on the command string.

⚑ EXTRACTED FROM `scratch/toolmodes.py` (⟡toolmodes-layers). This module RUNS and reports
verdicts; rendering is the caller's, so a case can drive every verdict without capturing stdout.
"""

from __future__ import annotations

import os
import subprocess
from dataclasses import dataclass
from typing import TYPE_CHECKING

from substrate import corpus

if TYPE_CHECKING:
    from collections.abc import Callable, Iterable

    from substrate.tool_decline import Decline

# The verdicts a decline can carry.
GUARDED = "GUARDED"
LAPSED = "LAPSED"
UNCHECKED = "UNCHECKED"
UNGUARDED = "UNGUARDED"
DECLARED = "declared"

# ⚑ THE DECLINE'S OWN BUDGET, deliberately separate from any other timeout in the toolkit: raising
# this must not loosen an unrelated one. Overridable because a slow host is a real state.
TIMEOUT_S = float(os.environ.get("SUBSTRATE_DECLINE_TIMEOUT_S", "900"))

# ⚑⚑ THE SHELL'S OWN "I COULD NOT RUN IT" CODES — 127 not found, 126 found but not executable.
# `shell=True` means a missing command does NOT raise: the shell runs successfully and reports
# 127, so a naive `returncode == 0` reads *"this refusal has lapsed"* over a machine that never
# executed the check. That is the environment-as-claim collapse this module exists to prevent.
UNRUNNABLE_CODES = frozenset({126, 127})

# ⚑⚑ SLOTTED DATACLASSES, NOT `NamedTuple` (⟡symbolic-reference-only). A `NamedTuple` subclasses
# `tuple`, so `decline, verdict, detail = row` and `row[0]` both work — numeric access to a thing
# that HAS NAMES, and a field reorder would silently rebind every such site. A slotted dataclass
# carries neither `tp_iter` nor the sequence protocol, so each positional site becomes a STATIC
# error naming its own line. `order=True` is absent: nothing here sorts these, and adding it would
# assert a by-declaration-order comparison nobody asked for.


@dataclass(frozen=True, slots=True)
class Verdict:
    """What running one decline's check established — or could not."""

    decline: Decline
    verdict: str
    detail: str

    @property
    def holds(self) -> bool:
        """Report whether this refusal is currently backed by a passing check."""
        return self.verdict == GUARDED

    @property
    def needs_attention(self) -> bool:
        """Report whether a reader must look — a lapse or an environment that could not verify.

        ⚑ UNGUARDED IS NOT INCLUDED, and that is deliberate: it is a standing property of the
        record rather than a change in the world. It is reported every run and counted separately,
        so it does not drown the two verdicts that mean *something happened*.
        """
        return self.verdict in (LAPSED, UNCHECKED)


@dataclass(frozen=True, slots=True)
class Report:
    """Every decline's verdict, and the counts a reader weighs them by."""

    verdicts: tuple[Verdict, ...]

    @property
    def guarded(self) -> int:
        """Return how many refusals are currently backed."""
        return sum(1 for v in self.verdicts if v.verdict == GUARDED)

    @property
    def lapsed(self) -> int:
        """Return how many checks ran and failed."""
        return sum(1 for v in self.verdicts if v.verdict == LAPSED)

    @property
    def unchecked(self) -> int:
        """Return how many could not run here — a fact about this environment."""
        return sum(1 for v in self.verdicts if v.verdict == UNCHECKED)

    @property
    def unguarded(self) -> int:
        """Return how many declare no check at all."""
        return sum(1 for v in self.verdicts if v.verdict == UNGUARDED)

    @property
    def exit_code(self) -> int:
        """Return 1 when a refusal stopped being verifiable, else 0.

        ⚑ UNCHECKED FAILS TOO, and that is the honest direction: a run that could not verify its
        refusals has not established that they hold, and reporting success would bank an
        unmeasured claim.
        """
        return 1 if (self.lapsed or self.unchecked) else 0


def _run(command: str) -> tuple[bool | None, str]:
    """Run one check and return `(passed, note)`; `None` means it could not run at all.

    ⚑⚑⚑ EXIT 127 IS UNCHECKED, NOT LAPSED, AND THIS MODULE HAD IT WRONG UNTIL A CASE SAID SO.
    `shell=True` means a missing command never raises, so the first cut reported *"this refusal
    has lapsed"* over a machine that had not executed the check — the environment-as-claim
    collapse this module is built to prevent, in the module itself. The suite caught it; a
    report would not have.

    ⚑ A TIMEOUT IS ALSO UNCHECKED, and arrives as an exception rather than a code — measured once
    on a host in POWERSAVE, where a corpus walk exceeded its budget and correctly reported
    UNCHECKED rather than a tree of apparent lapses.
    """
    try:
        done = subprocess.run(
            command,
            shell=True,
            cwd=str(corpus.ROOT),  # noqa: S602 — the check
            capture_output=True,
            text=True,  # IS a shell command, by
            timeout=TIMEOUT_S,
            check=False,
        )  # declaration
    except (OSError, subprocess.SubprocessError) as exc:
        return None, f"{type(exc).__name__}: {exc}"
    if done.returncode in UNRUNNABLE_CODES:
        return None, f"exit {done.returncode} — the shell could not run it"
    return done.returncode == 0, f"exit {done.returncode}"


def verify(
    declines: Iterable[Decline],
    *,
    quick: bool = False,
    announce: Callable[[str], None] | None = None,
) -> Report:
    """Return each decline's verdict, running its check unless `quick`.

    ⚑ `quick` IS NEVER THE DEFAULT. A listing that skips execution makes UNGUARDED and GUARDED
    indistinguishable — which is the exact failure the record type exists to prevent — so the
    cheap path must be asked for explicitly.

    ⚑ THE ANNOUNCE HOOK EXISTS BECAUSE A SILENT CORPUS WALK IS INDISTINGUISHABLE FROM A HUNG ONE.
    Several checks are real gates; saying which one is running before it runs is the difference
    between waiting and wondering.
    """
    ran: dict[str, tuple[bool | None, str]] = {}
    out: list[Verdict] = []

    for decline in declines:
        if decline.check is None:
            out.append(Verdict(decline=decline, verdict=UNGUARDED, detail="no check declared"))
            continue
        if quick:
            out.append(Verdict(decline=decline, verdict=DECLARED, detail=decline.check))
            continue

        if decline.check not in ran:
            if announce is not None:
                announce(decline.check)
            ran[decline.check] = _run(decline.check)

        passed, note = ran[decline.check]
        if passed:
            out.append(Verdict(decline=decline, verdict=GUARDED, detail=decline.check))
        elif passed is None:
            out.append(
                Verdict(
                    decline=decline,
                    verdict=UNCHECKED,
                    detail=f"{decline.check}  ⚑ did not run: {note}",
                )
            )
        else:
            out.append(
                Verdict(decline=decline, verdict=LAPSED, detail=f"{decline.check}  → {note}")
            )
    return Report(verdicts=tuple(out))
