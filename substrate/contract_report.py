# SPDX-License-Identifier:Apache-2.0
# Copyright 2026 Mike Mol
"""Render the mode-contract audit — the scan contract, roster drift, and opt collisions.

⚑⚑⚑ EXTRACTED FROM A 2,173-LINE DISPATCH ARM, WHICH IS THE DRAIN'S ACTUAL UNIT. Operator:
*"Draining is not editing in place, it is migrating code OUT, making it clean wherever it's
been migrated to, and then repointing consumers."* The origin's arm reads only module-level
names, so it was a function already — spelled as an `if` branch inside a function that does
seventy other things. Nothing here is new logic; what is new is that it has a name, a home, and
cases.

⚑⚑ THREE DEBTS ARE REPORTED SEPARATELY BECAUSE THEY ARE NOT THE SAME DEBT, and the origin's
own comments say so. A CONTRACT violation is "a declared promise is unmet"; a ROSTER
disagreement is "the declared modes and the dispatch disagree about what exists"; an opt
COLLISION is a known, judged-benign residue. Summing them would make a paydown of one read as
progress on all three, and folding the collisions into the failure count would fail a gate on
residue that was measured and declared.

⚑ AN EMPTY ROSTER IS NOT A PASS, and that is the load-bearing branch. Zero declared contracts
and zero violations render identically in a bare count — the confident-zero this whole family
of readers exists to close — so a census that measured nothing must say so rather than exit
clean.

⚑ THE RENDERING IS SEPARATE FROM THE VERDICT. A caller that wanted the exit code without the
output could not get it from the origin, because printing and deciding were one pass; here the
verdict is a value and the text is a string, so a gate can consume either.
"""

from __future__ import annotations

from dataclasses import dataclass

#: Every declared contract was honoured.
CLEAN = 0

#: At least one declared contract is unmet.
FAILED = 1

#: Nothing was measured — no mode declares the contract at all.
UNMEASURED = 2


@dataclass(frozen=True, slots=True)
class Row:
    """One mode's contract verdict.

    ⚑ `ok` IS KEYWORD-ONLY BECAUSE A POSITIONAL BOOLEAN IS TRANSPOSABLE. `Row(flag, True,
    why)` and a future `Row(flag, why, True)` are both well-formed calls, and the rule that
    catches this (`FBT003`) is not style: a silently transposed verdict would score a passing
    mode as failing with the reason and the flag intact, which reads entirely plausible.
    """

    flag: str
    why: str
    ok: bool | None = None

    @property
    def mark(self) -> str:
        """The three-state label — ok, unknown, or failed.

        ⚑ UNKNOWN IS ITS OWN STATE, NOT A FAILURE. A mode this reader could not resolve is a
        fact about the reader; scoring it as a violation would report a blind spot as debt.
        """
        if self.ok is None:
            return "UNK "
        return "ok  " if self.ok else "FAIL"


def verdict(rows: list[Row]) -> int:
    """Return the exit code for a set of contract rows.

    ⚑⚑ AN EMPTY ROSTER EXITS UNMEASURED, NEVER CLEAN. Zero violations over zero contracts is
    indistinguishable from zero violations over many, and a gate that reported the first as a
    pass would be green precisely when it had checked nothing.
    """
    if not rows:
        return UNMEASURED
    return FAILED if any(r.ok is False for r in rows) else CLEAN


def failures(rows: list[Row]) -> list[Row]:
    """Return the rows whose declared contract is unmet.

    ⚑ `ok is False`, NOT `not ok`. An UNKNOWN row is falsy and is not a failure — collapsing
    the two would score this reader's blind spots as the subject's debt.
    """
    return [r for r in rows if r.ok is False]


def partition(rows: list[Row], contract_flags: set[str]) -> tuple[list[Row], list[Row]]:
    """Split rows into contract rows and roster/dispatch disagreements.

    ⚑ A ROSTER ROW HAS NO DECLARED CONTRACT TO QUOTE, and assuming it did crashed the
    origin's printer on its first run. The rows reporting dispatched-but-undeclared flags are
    exactly the ones absent from the roster, so any lookup keyed on the roster is guaranteed
    to fail for precisely the finding — a reporter that cannot render its own new verdict.
    """
    contract = [r for r in rows if r.flag in contract_flags]
    roster = [r for r in rows if r.flag not in contract_flags]
    return contract, roster


def render(
    rows: list[Row], contract_flags: set[str], collisions: list[tuple[str, list[str], bool, str]]
) -> str:
    """Render the full audit: per-row marks, the two counts, and the collision residue."""
    out = [f"  {r.mark} {r.flag:<20} {r.why}" for r in rows]

    contract, roster = partition(rows, contract_flags)
    honoured = len(contract) - len([r for r in contract if r.ok is False])
    out.append(
        f"{honoured} of {len(contract)} declaring mode(s) honour the incomplete-scan contract"
    )
    if roster:
        out.append(
            f"{len(roster)} roster/dispatch disagreement(s) — the roster is the "
            f"declared authority and the dispatch is what runs"
        )

    if collisions:
        harmful = [c for c in collisions if c[2]]
        out.append(f"{len(collisions)} spelling(s) are BOTH a roster key and another mode's opt:")
        for flag, owners, harm, why in collisions:
            out.append(f"  {'HARM' if harm else 'ok':<4} {flag:<16} opt-of {' '.join(owners)}")
            out.append(f"       {why}")
        # ⚑ REPORTED AND DELIBERATELY NOT SCORED. These are a known miss in the opt
        # validator, judged benign and declared; folding them into the failure count would
        # fail a gate on residue somebody already adjudicated.
        out.append(
            f"  {len(harmful)} harmful (different meaning per role) — 0 is the "
            f"paydown target; the rest are BENIGN and stay."
        )

    if not rows:
        out.append("   ⚑ NO mode declares the contract — this gate measured NOTHING.")
    return "\n".join(out) + "\n"
