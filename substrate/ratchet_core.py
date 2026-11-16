#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Mike Mol
"""What is TRUE about a census against its baseline — the three verdicts, no rendering.

The last piece of ⟡ratchet-seams. Seven modules came out of `ratchet.py` before this
one; what remains here is only the comparison itself.

⚑⚑ THE ARITY RULE FOUND ONE DEFECT AT SIX SCALES, and this file is where it bottoms out.
`PLR0913` fired on `log_fallthrough` (payload -> `Refusal`), `check_argv` (transposable
booleans -> keyword-only), `_compare` (eight threaded -> `Run`), `set_ratchet` (twelve,
then seven -> `Census`), and `ratchet_render`'s functions (`label`+`report` -> `Voice`).
Every time the fix was the same move: **a parameter list that long is a value nobody
named.** Reading it as a style rule and carrying the finding would have left the census
itself nameless.

⚑ AND THE SEVENTH SPLIT WAS THE GATE'S ADVICE TAKEN LITERALLY. This module reached one
remaining `ISC004` and the reflex was to rewrite four hundred lines to fix one string.
Operator: *"each time you can't manage to get something past the harness, decompose it;
it really is a sign you're doing too much in one file."* The refusal was never asking for
a better line — it was reporting that presentation and verdict logic shared a module.
"""

from __future__ import annotations

import sys
from dataclasses import dataclass, replace
from pathlib import Path
from typing import TYPE_CHECKING

from mikemol.ratchet import render

from substrate.baseline_io import (
    MINT_BYPASS,
    may_write,
    read_baseline,
    split_moves,
    write_baseline,
)

if TYPE_CHECKING:
    from collections.abc import Callable, Iterable


@dataclass(frozen=True, slots=True)
class Census:
    """The thing under ratchet: its keys, where its baseline lives, and its grammar.

    ⚑⚑ THIS IS THE VALUE WHOSE ABSENCE FORCED AN EITHER/OR. `set_ratchet` took seven
    arguments and the choice looked like "bundle at twenty call sites" or "carry the
    finding" — both of which take the parameter list as given. Underneath, three of the
    seven were one thing: WHAT census, WHERE its baseline is, WHAT to call it.

    ⚑ `key_move` BELONGS HERE, NOT WITH THE RUN. The original docstring says it exactly:
    *"`key_move` is supplied BY THE GATE (only the gate knows its key grammar)"* — a
    property of the CENSUS, constant across every run of that gate, not a per-run option.
    """

    keys: set[str]
    baseline_path: str
    label: str
    key_move: Callable[[str], str] | None = None

    @classmethod
    def of(
        cls,
        keys: Iterable[str],
        baseline_path: str,
        label: str,
        key_move: Callable[[str], str] | None = None,
    ) -> Census:
        """Build a census from the legacy positional arguments.

        ⚑ THE ADAPTER SEAM. Twenty call sites across sixteen gates pass exactly these
        four, so `ratchet.py`'s shim calls this and hands the result on — no gate changes.
        """
        return cls(keys=set(keys), baseline_path=baseline_path, label=label, key_move=key_move)


@dataclass(frozen=True, slots=True)
class Permission:
    """What this particular run may do to the baseline."""

    write: bool
    dry: bool

    @classmethod
    def resolve(
        cls, argv: list[str], *, write: bool | None = None, dry_run: bool | None = None
    ) -> Permission:
        """Resolve the write question from explicit intent, argv, and the environment.

        ⚑ `--dry-run` IS RESOLVED HERE, NOT FORWARDED BY TEN CALL SITES. Threading one
        flag through ten files is the shape this arc keeps retiring: N call sites doing
        what the authority can do once, and the ELEVENTH gate written next month would
        silently lack it. An explicit `dry_run=` still wins, for a non-CLI caller.

        ⚑ AND A DRY RUN CANNOT WRITE, BY CONSTRUCTION rather than by every branch
        remembering to check both booleans.
        """
        dry = ("--dry-run" in argv[1:]) if dry_run is None else bool(dry_run)
        return cls(write=False if dry else may_write(write=write), dry=dry)


@dataclass(frozen=True, slots=True)
class Diff:
    """One census against its baseline, partitioned into the three verdicts.

    ⚑ THEY ARE GENUINELY INDEPENDENT: a run can relocate AND pay down AND grow, and each
    means something different to the operator. A move is not paydown (the debt still
    exists) and not growth (the total did not rise). Collapsing them into one function is
    what made an earlier cut `C901`-complex.
    """

    added: set[str]
    paid: set[str]
    moved: set[tuple[str, str]]


def partition(cur: set[str], base: set[str], key_move: Callable[[str], str] | None) -> Diff:
    """Split the census-vs-baseline difference into moves, paydown and growth."""
    added = cur - base
    paid = base - cur
    moved, added = split_moves(added, paid, key_move)
    return Diff(added=added, paid=paid - {src for src, _dst in moved}, moved=moved)


def mint(census: Census, voice: render.Voice, permission: Permission) -> int:
    """Record a baseline that does not exist yet; verify it round-trips.

    ⚑⚑ A WRITE MUST CONFIRM WHAT LANDED, NOT WHAT WAS INTENDED, and a write succeeding is
    not a read AGREEING. A serializer that drops a key containing a newline, or a reader
    that strips differently, is invisible to "the write did not raise". A census can
    verify presence, never behaviour — and minting a paydown-only baseline is the least
    recoverable moment there is: a wrong one is debt that can never legitimately be paid.

    ⚑ THE BYPASS WARNING IS SUPPLIED HERE, ONCE, for every gate: this is the one call site of
    `no_baseline_lines`, and mtools' default text does not name this repo's write switch. A gate
    that set its own `mint_bypass` keeps it.
    """
    cur, path = census.keys, census.baseline_path
    if not permission.write:
        if voice.report.mint_bypass is None:
            voice = replace(voice, report=replace(voice.report, mint_bypass=MINT_BYPASS))
        render.emit(render.no_baseline_lines(len(cur), path, voice))
        return 0
    write_baseline(path, cur)
    back = read_baseline(path)
    if back != cur:
        render.emit(render.roundtrip_failure(cur - back, back - cur, (len(cur), len(back)), voice))
        return 1
    render.emit([render.recorded_line(len(cur), len(back), path, voice)])
    return 0


def rule(census: Census, base: set[str], voice: render.Voice, permission: Permission) -> int:
    """Rule on a census against an existing baseline. 0 = pass, 1 = debt grew."""
    diff = partition(census.keys, base, census.key_move)
    verb = "LOWERED" if permission.write and not diff.added else "would lower"
    lines = [
        *render.moved_lines(diff.moved, voice),
        *render.paid_lines(
            diff.paid, (len(base), len(census.keys)), voice, verb=verb, dry=permission.dry
        ),
        *render.added_lines(diff.added, len(diff.paid), voice),
    ]

    # ⚑ THE WRITE IS DECIDED HERE, NOT INSIDE A RENDERER. A renderer that also wrote would
    # make the message and the side effect inseparable, so a `--list` or `--quiet` run
    # could bank a baseline as a side effect of formatting. A run that is ONLY relocation
    # must still record, or the baseline stays pinned to paths that no longer exist; one
    # move consumes one removal, so it cannot lower the debt.
    if permission.write and not diff.added and (diff.paid or diff.moved):
        write_baseline(census.baseline_path, census.keys)

    if diff.added:
        render.emit(lines)
        return 1
    if not diff.paid and not voice.report.quiet:
        lines.append(render.frozen_line(len(base), voice))
    if lines:
        render.emit(lines)
    return 0


def set_ratchet(
    census: Census, report: render.Report = render.DEFAULT, permission: Permission | None = None
) -> int:
    """Run the paydown-only ratchet over `census`. 0 = pass, 1 = debt grew.

    ⚑ WRITING IS OPT-IN, because a census READ must not bank debt. MEASURED TWICE:
    simply running `check_sumtype_ratchet.py --quiet` — no commit, no `--apply` — rewrote
    its baseline 48 -> 45. The second time it was a READ-ONLY auditor that had been
    explicitly forbidden to write and could not avoid it. A transient dip is then banked
    PERMANENTLY: the paid-down keys can never return without the gate REFUSING, so a gate
    that mis-parses launders its own bug into the baseline.

    ⚑ THREE ARGUMENTS, EACH A NAMED VALUE: what is under ratchet, how it reads, what this
    run may do.
    """
    voice = render.Voice(label=census.label, report=report)
    perm = Permission.resolve(sys.argv) if permission is None else permission

    if report.list_keys:
        render.emit(render.census_listing(census.keys, voice))
        return 0

    if not Path(census.baseline_path).exists():
        return mint(census, voice, perm)
    return rule(census, read_baseline(census.baseline_path), voice, perm)
