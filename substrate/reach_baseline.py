#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Mike Mol
"""Persist the per-suite reach census: the last ACCEPTED reading, as a pair.

⚑⚑ THE SECOND DAG LAYER OF ⟡may-write-convention, extracted leaves-first. `reach_ratchet`
holds the one-character fix a live `TypeError` needs, and it sits above this pair plus
`reach_verdict`; neither can move before its callees have. The 1834-finding file they came
from refuses every edit, so the route is extraction rather than repair in place.

⚑ A PAIR, NOT A SCALAR, AND THAT IS WHAT MAKES IT RAGGED-SAFE. The refusal is a PREDICATE over
both lenses (`reach_verdict`), so nothing here needs to be a maximum.

⚑⚑⚑ IT IS DELIBERATELY NOT A HIGH-WATER MARK, and the code once said otherwise while doing
the right thing. Until 2026-08-25 the write loop had TWO BYTE-IDENTICAL ARMS, with the `else`
commented *"the high-water LOWERS, deliberately and only here"* — a comment describing a
discrimination the branch did not make, so a reader audited the polarity against a conditional
that had none.

⚑⚑ AND THE COLLAPSE IS THE CORRECT SEMANTICS, NOT A LOST ONE. A high-water mark is a SCALAR
COLLAPSE OF A PREDICATE OVER A SET, expressible only when the done-set is a PREFIX — it buys
that by ASSERTING prefix-closure rather than carrying it. Suite reach is not a prefix, and the
record proves it four times: `tmi_subject` runs 11 of a hardcoded 15 (four need a corpus that
may be absent), `jea_circuit`'s 300 is a keyword DEFAULT that `trials=50` moves with the
source byte-identical, five suites read a static 0 purely because `CASE_CALLS` had not learned
`ok`/`chk`, and three reported SILENT while passing. A max over readings like those banks
whichever configuration happened to be richest and refuses every honest run thereafter.

⚑ WHICH IS WHY THE MINTING ORDER DOES NOT MATTER, and that is the observable proof the scalar
is gone. Under a true HWM the ORDER OF TWO UNRELATED EVENTS (widening `CASE_CALLS` vs minting)
would fix a permanent floor: mint-first banks five permanent zeros, widen-first banks a mark a
leaner config cannot reach. **Both directions failing is the tell that the scalar was WRONG
rather than mis-set.**
"""

from __future__ import annotations

from pathlib import Path

# A recorded row: (cases the run reached, static call sites the source holds).
Reading = tuple[int, int | None]

# Written at the head of every minted file, so a reader who opens it learns the semantics
# without finding this module first.
_HEADER = (
    "# ⟡selftest-reach — per-suite LAST ACCEPTED reading, as a PAIR.\n"
    "# NOT a high-water mark: nothing is gated on this being a maximum. A\n"
    "# suite may gain cases freely; losing them REFUSES unless the SECOND\n"
    "# column shows the call sites went with them. The refusal is the\n"
    "# two-lens predicate in `reach_verdict`, not an inequality against a\n"
    "# stored max — so a row lowers whenever a run is accepted, and the\n"
    "# order this file was first minted in does not fix a floor.\n"
    "# Derived, never hand-edited.\n"
    "# label\treached\tstatic-call-sites\n"
)

# A row is `label \t reached \t static`, the third column optionally empty.
_MIN_FIELDS = 2


def _row(parts: list[str]) -> tuple[str, Reading] | None:
    """Parse one TSV row, or None when it is not a reading.

    ⚑ A MALFORMED ROW IS SKIPPED, NOT RAISED. This file is derived and rewritten on every
    accepted run; a partial write or a hand edit must degrade to a missing row — which
    `reach_verdict` reads as `new` and records — rather than crashing the gate. A gate that
    CRASHES is strictly worse than one that refuses: the traceback is not a verdict.
    """
    if len(parts) < _MIN_FIELDS or not parts[1].isdigit():
        return None
    static = parts[2] if len(parts) > _MIN_FIELDS else ""
    return (parts[0], (int(parts[1]), int(static) if static.isdigit() else None))


def read_reach(path: str) -> dict[str, Reading]:
    """Return the last accepted reading per suite. An unreadable file reads as empty.

    ⚑ EMPTY IS THE CORRECT DEGRADATION, because every row then classifies as `new` — recorded,
    never refused. A first sighting is not a loss, so a missing baseline cannot manufacture
    one.
    """
    out: dict[str, Reading] = {}
    try:
        text = Path(path).read_text(encoding="utf-8")
    except OSError:
        return out
    for line in text.splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue
        parsed = _row(stripped.split("\t"))
        if parsed is not None:
            out[parsed[0]] = parsed[1]
    return out


def write_reach(path: str, census: dict[str, Reading]) -> None:
    """Write the census, sorted, with the semantics stated in its own header."""
    rows = "".join(
        f"{label}\t{total}\t{'' if static is None else static}\n"
        for label in sorted(census)
        for total, static in [census[label]]
    )
    Path(path).write_text(_HEADER + rows, encoding="utf-8")
