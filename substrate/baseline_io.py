#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Mike Mol
"""Persist a ratchet baseline, and decide what a run is permitted to do to it.

Extracted from `ratchet.py` as part of ⟡ratchet-seams: reading and writing the baseline,
resolving whether writing is permitted at all, and partitioning a decomposition's
relocations out of its genuine additions. All three are separable from the verdict logic
that consumes them, and separating them is what leaves `set_ratchet` small enough to
author cleanly.

⚑ THE CASES LIVE IN `baseline_io_selftest.py`, NOT IN THIS FILE'S TAIL (⟡n-split-the-tails).
They were inline until a coverage census counted that as a convention rather than as debt;
operator: *"n-split that crap. No more in-line/tail testing."* Inline cases cannot run without
importing the module under test, and a module too dirty to edit takes its own suite hostage.
The move grammar `_ident` went with them — it was only ever the test's stand-in for the key
grammar a real gate supplies itself.
"""

from __future__ import annotations

import os
from collections import defaultdict
from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from collections.abc import Callable, Iterable

# The environment switch `may_write` reads when no explicit intent is given.
WRITE_SWITCH = "SUBSTRATE_RATCHET_WRITE"

# ⚑ THE BYPASS WARNING NAMES THIS REPO'S SWITCH, SO IT LIVES BESIDE THE SWITCH. mtools'
# `mikemol.ratchet.render` has no such switch (its write is an explicit `write=True`) and its
# default text no longer names one; a gate here passes this as `Report.mint_bypass` until the
# gates move off the environment switch (W38b).
MINT_BYPASS = (
    f"  Setting {WRITE_SWITCH}=1 by hand BYPASSES that gate and banks a census\n"
    "  against a tree nothing has approved — the `--no-verify` shape. Enumerate first:  "
    "--list"
)


def may_write(*, write: bool | None = None) -> bool:
    """Report whether this process may rewrite a baseline. THE single resolver.

    ⚑ THE GUARD MUST NOT BE RE-DERIVED PER GATE. `set_ratchet` grew this guard after the
    read-mutates-state defect was MEASURED TWICE — but `set1_ratchet_cores.py` kept its
    own hand-rolled census gate and therefore never got it, so a plain `--quiet` run of
    that one gate banked debt permanently. **The fix applied to the abstraction but not
    to the one member that opted out of it**, and it is invisible *because* the
    surrounding convention is so well-articulated.

    ⚑⚑ THE SECOND-ORDER DAMAGE IS WORSE THAN THE FIRST. The standing instruction "do not
    run the ratchet gates, they mutate" became TRUE OF ONE GATE AND FALSE OF SIX, and
    nobody could tell which — so it trained avoidance of a whole class for a reason that
    no longer applied to most of it. Exporting the resolver is what makes the instruction
    true again, uniformly.

    ⚑ `write` IS KEYWORD-ONLY, AND THAT CHOICE IS CORRECT. `FBT001` refuses a boolean
    positional because a bare `may_write(True)` says nothing at the call site about what the
    True means — and this particular boolean decides whether a gate WRITES.

    ⚑⚑ BUT THE CLAUSE THAT USED TO FOLLOW IT WAS STALE, AND IT WENT STALE INSIDE THE FILE
    WHOSE JOB IS TO BE THE SINGLE RESOLVER. This docstring read *"the three existing callers
    keep working against `ratchet.may_write`; a caller migrating here names it"* — TRUE WHEN
    WRITTEN, describing a positional `ratchet.may_write` sitting beside a keyword-only one
    here. ⟡gate-island-promote then repointed the facade at THIS function, so
    `ratchet.may_write` and `may_write` became the same object and the divergence the sentence
    rested on ceased to exist. The sentence did not become false about the code it described;
    the code it described stopped being there, which is the harder kind to notice.

    ⚑⚑⚑ AND IT COST A LIVE GATE. `scripts/run_selftests.py:724` calls `may_write(write)`
    positionally and raises `TypeError` — crashing `run_selftests --selftest`, a Phase A gate —
    while this docstring stated the callers were fine. A REASSURANCE IS THE WORST THING TO GO
    STALE: a reader checking whether the migration was safe found a sentence saying it was, and
    that sentence is exactly what a `--forwards may_write write` census would have falsified in
    one call. Measured: 4 of 9 call sites forward the keyword. The four that do not pass NO
    argument at all and are unaffected; the ONE genuine positional besides 724 is
    `tests/test_rederive_agreement.py:202`, whose file carries 165 findings and is likewise
    frozen. **The claim is not restated here in a corrected form** — a per-call-site status
    belongs in the census that derives it, not in prose that must be re-edited to stay true.
    """
    if write is None:
        return os.environ.get(WRITE_SWITCH) == "1"
    return bool(write)


def write_baseline(path: str, keys: Iterable[str]) -> None:
    """Write `keys` to `path`, one per line, sorted."""
    Path(path).write_text("".join(f"{k}\n" for k in sorted(keys)), encoding="utf-8")


def read_baseline(path: str) -> set[str]:
    """Read `path` as a set of keys, ignoring blank lines."""
    return {ln.strip() for ln in Path(path).read_text(encoding="utf-8").splitlines() if ln.strip()}


def split_moves(
    added: set[str],
    paid: set[str],
    key_move: Callable[[str], str] | None,
) -> tuple[set[tuple[str, str]], set[str]]:
    """Partition `added` into (relocations, genuine additions).

    ⚑ THE SET RATCHET HAS NO VOCABULARY FOR A MOVE, AND THE MODULE ALREADY SAID SO.
    `set_ratchet`'s own docstring records it: *"a decomposition (which retires an old
    path-key and mints a new one for a byte-identical line) always presents as 'added'."*
    That was half-fixed — paydown stopped being HIDDEN by an addition — but the addition
    still REFUSES, so a repo that decomposes files as policy makes its own re-export gate
    permanently red. MEASURED on `public-ratchet`: 139 genuine paydowns blocked from
    recording behind ~100 keys that are the SAME debt carried through a split
    (`Quotient.agda::Canonical` -> `Quotient/Canonical.agda::Canonical`).

    ⚑⚑ A PERMANENTLY-RED GATE IS A DISABLED GATE, and that is the actual failure. It
    cannot distinguish the new offence from the backlog, so the next genuine re-export
    lands invisibly among a hundred relocations — the gate reports BROKEN either way,
    which is the same information as reporting nothing. This is the ratchet analogue of a
    census whose green is a fact about the census.

    ⚑ WHAT MAKES A MOVE CREDITABLE, and it is deliberately narrow. `key_move` is supplied
    BY THE GATE (only the gate knows its key grammar) and must return a comparable
    identity — for a `<relpath>::<opened>` key, the opened name. A pairing counts only
    when the identity matches a key being REMOVED in the same run, AND it is ONE-TO-ONE:
    a 1->N fan-out is NOT a move. Splitting one re-export into eight is eight re-exports;
    crediting it as a move would launder real growth through the decomposition channel,
    which is the swap-gaming the SET form exists to catch.

    So the total can never RISE through this path: each move consumes exactly one
    removal. A gate that passes no `key_move` is unchanged in every respect.
    """
    if key_move is None or not added or not paid:
        return set(), added
    src_by: dict[str, list[str]] = defaultdict(list)
    for k in paid:
        src_by[key_move(k)].append(k)
    dst_by: dict[str, list[str]] = defaultdict(list)
    for k in added:
        dst_by[key_move(k)].append(k)
    moves: set[tuple[str, str]] = set()
    for ident, dsts in dst_by.items():
        srcs = src_by.get(ident, [])
        # ⚑ ONE-TO-ONE ONLY. A 1->N fan-out is genuine growth wearing a move's clothes;
        # N->1 is a genuine paydown and must stay visible as one.
        if len(dsts) == 1 and len(srcs) == 1:
            moves.add((srcs[0], dsts[0]))
    return moves, added - {d for _s, d in moves}
