#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Mike Mol
"""Report every ratchet gate's paydown standing in one pass.

⚑⚑ THIS EXISTS BECAUSE THE JUDGEMENT WAS HAPPENING IN THE TURN. Four gates were hand-read,
twice, by running each and eyeballing its paydown line — and a `| head` over the fifth was
correctly refused: a pipeline that extracts a number from a tool's output IS the reasoning,
and it evaporates when the turn ends. Nineteen gates read by hand is nineteen chances to
mis-transcribe and no chance for the next reader to reproduce the total.

⚑ AND THE TOTAL IS THE POINT, NOT THE ROWS. "Nineteen gates are red" is ONE defect reported
nineteen times when every blocking addition is a decomposition child whose parent survives.
Summing `paid` across gates makes the size of what the additions are holding visible; reading
them one at a time never does.

⚑ REPORTING ONLY — `gate_probe` owns the running, and with it the subprocess exemption. This
module runs nothing, so nothing here can grow into a second place that does.
"""

from __future__ import annotations

import sys

from scripts import gate_probe


def _line(row: gate_probe.Row) -> str:
    """Render one gate's standing."""
    if not row.ran:
        return f"  {row.gate:<44} UNREAD"
    if row.blocked:
        return f"  {row.gate:<44} {row.paid:>7} paid  HELD by {row.added} new"
    if row.added:
        return f"  {row.gate:<44} {'':>7}       BROKEN — {row.added} new"
    if row.paid:
        return f"  {row.gate:<44} {row.paid:>7} paid  ({row.before} -> {row.after})"
    return f"  {row.gate:<44} {'':>7}       steady"


def _rank(row: gate_probe.Row) -> tuple[int, str]:
    """Sort key: most paydown first, then by name.

    ⚑ A NAMED FUNCTION, NOT A LAMBDA — the same finding `haskell_escape._codepoint` records.
    `sorted`'s `key=` is typed over an unbound parameter, so a lambda's `r` is `Any` and the
    tuple it builds is `Any` with it: three findings from one expression. Declaring the
    parameter types the whole thing, and it reads better than the lambda did.
    """
    return (-row.paid, row.gate)


def report(rows: list[gate_probe.Row]) -> list[str]:
    """Render the census, most paydown first — that is where the work is."""
    ranked = sorted(rows, key=_rank)
    blocked = [r for r in ranked if r.blocked]
    held = sum(r.paid for r in blocked)
    adds = sum(r.added for r in blocked)
    tail = f"  ⚑ {held} key(s) of paydown held by {adds} addition(s) across {len(blocked)} gate(s)."
    return [f"paydown-census: {len(ranked)} gate(s)", *(_line(r) for r in ranked), tail]


def main() -> int:
    """Measure every gate and print the census. Always 0 — this reports, it does not rule."""
    rows = [gate_probe.measure(g) for g in gate_probe.gates()]
    sys.stdout.write("\n".join(report(rows)) + "\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
