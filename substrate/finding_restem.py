#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Mike Mol
"""Pair an unpaired WITNESS key with an unpaired BIB key that is the same finding.

⚑⚑⚑ THE THIRD DRAIN UNIT, AND IT IS THE READER THAT SAVED THE PAIRING CENSUS FROM ITSELF.
`--pairing` reported 20 witness-only and 10 bib-only rows, and four of each were THE SAME FOUR
FINDINGS: `tmi-F6` is a bare stem in the roster and `tmi-F6-ground-truth-reduced-to-count-…`
in the bib. One finding, two spellings, counted twice on OPPOSITE sides of one report — which
is `census-keyed-on-one-spelling` occurring inside the census built to find that class. A
naive paydown reading thirty rows as thirty findings files four duplicate bib entries and four
duplicate witnesses: **the drift GROWING through the instrument built to shrink it.**

⚑⚑ THE RELATION IS `bib.startswith(witness + "-")` AND THE TRAILING HYPHEN IS LOAD-BEARING.
Without it `tmi-F1` prefixes `tmi-F10`, so two unrelated findings marry and the report asserts
a spelling relation between different subjects — the ambiguity `finding_resolve` refuses
rather than guesses, arriving one reader over.

⚑⚑ AND A PREFIX MATCH IS STILL NOT A PAIR WHEN THE STEM IS ALREADY SPOKEN FOR. `proc-F1` and
`proc-F2` are bib-only while the roster holds `proc-F1-cpu-floor-cannot-see-abandonment` and
`proc-F2-times-is-not-a-read` — but those witnesses are PAIRED, with their own bib entries, and
are about different subjects. Only an UNPAIRED key on each side can be one finding under two
spellings; a paired key on either side means the stem is REUSED, which is a key-allocation
defect and not a spelling.

⚑ AMBIGUITY IS REPORTED, NEVER RESOLVED. If one unpaired stem prefixes several unpaired bib
keys, no rule picks one — the row stays in the honest witness-only list rather than being
silently married to a guess.

⚑⚑⚑ WHAT THIS READER CANNOT DO IS PAY THE DRIFT DOWN (gate-G54). It correctly reduces the raw
count to TRUE DRIFT, and the remedy it names — re-key so the two spellings agree — requires
editing the roster, which is what the drain this module is part of exists to make possible.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from collections.abc import Iterable, Sequence

Pair = tuple[str, str]
Split = tuple[list[Pair], list[str], list[str]]


def restem(no_entry: Iterable[str], no_witness: Iterable[str]) -> Split:
    """Split two unpaired lists into `(spelling pairs, true witness-only, true bib-only)`.

    ⚑ A PAIR CONSUMES BOTH SIDES. A bib key matched by one stem is removed from the bib-only
    list, so the same finding is never reported as both a pair and a remainder — which would
    reintroduce the double-count this reader exists to remove.
    """
    witnesses = list(no_entry)
    bibs = list(no_witness)
    pairs: list[Pair] = []
    used: set[str] = set()
    for witness in witnesses:
        hits = [bib for bib in bibs if bib.startswith(witness + "-")]
        # ⚑ EXACTLY ONE, OR NOTHING. Several hits is an ambiguity to REPORT, and picking any
        #   of them would assert a spelling relation the evidence does not carry.
        if len(hits) == 1:
            pairs.append((witness, hits[0]))
            used.add(hits[0])
    paired = {witness for witness, _ in pairs}
    return (pairs,
            [key for key in witnesses if key not in paired],
            [key for key in bibs if key not in used])


def true_drift(split: Split) -> int:
    """Return the number of distinct findings the split reports as drifting.

    ⚑⚑ A PAIR COUNTS ONCE, WHICH IS THE WHOLE CORRECTION. The raw sum of the two unpaired
    lists double-counts every spelling pair, and that inflated figure is what a paydown would
    have acted on. Reporting both numbers lets a reader see the reduction rather than trust it.
    """
    pairs, witness_only, bib_only = split
    return len(pairs) + len(witness_only) + len(bib_only)


def raw_rows(no_entry: Sequence[str], no_witness: Sequence[str]) -> int:
    """Return the UNREDUCED row count, so the reduction is legible beside the result."""
    return len(no_entry) + len(no_witness)
