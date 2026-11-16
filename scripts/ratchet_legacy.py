#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Mike Mol
"""The twelve-argument `set_ratchet` every gate already calls, folded onto the new one.

⚑⚑ THIS MODULE EXISTS SO THAT ITS EXEMPTION CAN BE HONEST. The legacy signature takes
twelve arguments because TWENTY CALL SITES ACROSS SIXTEEN GATES pass twelve arguments;
`PLR0913`/`PLR0917`/`FBT001` are correct about the shape and cannot be satisfied without
changing every caller. Left in `ratchet.py`, that finding would have made the whole
compatibility face permanently unclean — and left in `ratchet_core`, it would have
granted the exemption to the verdict logic too.

⚑ A `per-file-ignores` ENTRY IS ONLY HONEST WHEN THE FILE HAS ONE RESPONSIBILITY, and
this file's responsibility IS the legacy face. The entry is deletable: it goes when the
last call site moves to `Census.of(...)`, and until then its presence in
`pyproject.toml` is the reminder that the migration is unfinished. That is the
difference between an exemption and a concession.

⚑⚑ AND THE SPLIT WAS THE HARNESS'S ADVICE, FOR THE THIRD TIME IN THIS ARC. `ratchet.py`
refused with the legacy signature inline; the reflex was to add the exemption there.
Operator: *"each time you can't manage to get something past the harness, decompose it;
it really is a sign you're doing too much in one file."* A file that is both an adapter
and a re-export surface is doing two things, and the refusal said so.
"""

from __future__ import annotations

import sys
from typing import TYPE_CHECKING

from mikemol.ratchet.render import Report

from substrate.ratchet_core import Census, Permission
from substrate.ratchet_core import set_ratchet as _rule

if TYPE_CHECKING:
    from collections.abc import Callable, Iterable


def set_ratchet(
    cur: Iterable[str],
    baseline_path: str,
    label: str,
    quiet: bool = False,
    noun: str = "entries",
    refuse_hint: str | None = None,
    write: bool | None = None,
    list_keys: bool = False,
    render: Callable[[str], str] | None = None,
    summary: str | None = None,
    dry_run: bool | None = None,
    key_move: Callable[[str], str] | None = None,
) -> int:
    """Run the paydown-only ratchet. 0 = pass, 1 = a NEW key appeared (debt grew).

    ⚑ THE SIGNATURE IS KEPT VERBATIM SO NO GATE CHANGES. Every argument folds into one
    of the three values `ratchet_core.set_ratchet` takes — WHAT is under ratchet
    (`Census`), how it READS (`Report`), and what this run MAY DO (`Permission`).

    ⚑ AN ADAPTER IS THE HONEST FORM OF A COMPATIBILITY LAYER. The alternative was
    bundling at twenty call sites in sixteen files; the alternative to THAT was carrying
    the finding forever. Neither was necessary once the census had a name — which is the
    point at which an either/or usually dissolves.
    """
    census = Census.of(cur, baseline_path, label, key_move)
    report = Report(
        noun=noun,
        render=render,
        summary=summary,
        refuse_hint=refuse_hint,
        quiet=quiet,
        list_keys=list_keys,
    )
    permission = Permission.resolve(sys.argv, write=write, dry_run=dry_run)
    return _rule(census, report, permission)
