#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Mike Mol
"""The shared SET-based paydown-only ratchet — the compatibility face of ten modules.

A recurring gate over ACCUMULATING DEBT — a census that should trend to 0 or hold — is a
RATCHET over a MATERIALIZED census: a baseline that pays down monotonically.

Semantics (unchanged):

  · no baseline yet   -> record the current set, pass.
  · a NEW key         -> REFUSE (debt may only be paid down, not grown).
  · a paid-down key   -> AUTO-LOWER: rewrite the baseline, pass.
  · unchanged         -> frozen at baseline, pass.

A SET (not a bare count) baseline also catches swap-gaming: remove one, add another, and
the added key is refused.

⚑⚑ THIS FILE IS NOW A RE-EXPORT SURFACE, AND EVERY CAPABILITY IT HELD LIVES IN ITS OWN
MODULE. ⟡ratchet-seams took 1,416 lines carrying seven unrelated responsibilities down to
this: VictoriaLogs ingest (`ratchet_log`), flag contracts (`ratchet_flags`), process-tree
recursion detection (`proc_ancestry`), withheld verdicts (`withheld_verdict`), the
baseline state vocabulary (`baseline_state`), baseline persistence (`baseline_io`),
message rendering (`ratchet_render`), the comparison itself (`ratchet_core`), its cases
(`ratchet_core_selftest`), the suite roster (`ratchet_suites`), and the twelve-argument
legacy signature (`ratchet_legacy`).

⚑ THE DECOMPOSITION WAS FORCED BY THE PER-FILE GATE AND THAT TURNED OUT TO BE RIGHT. At
215 findings this file refused EVERY edit, including the rewires that would have
completed each extraction — so the only route was N new modules at zero findings each,
composed. Operator: *"you don't need a single pass if you have multiple modules"*, and
*"each time you can't manage to get something past the harness, decompose it; it really
is a sign you're doing too much in one file."* The second fired FOUR times and was right
four times: it turned a four-hundred-line rewrite over one string into a clean split, it
separated the legacy signature so its exemption could be scoped to one responsibility,
and it moved the suite roster out of a file whose job is re-exporting.

⚑⚑ AND `PLR0913` FOUND ONE DEFECT AT SIX SCALES ALONG THE WAY. It fired on
`log_fallthrough` (payload -> `Refusal`), `check_argv` (transposable booleans ->
keyword-only), `_compare` (eight threaded -> `Run`), `set_ratchet` (twelve, then seven ->
`Census` + `Permission`), and every renderer (`label`+`report` -> `Voice`). It is not an
arity rule; it detects a VALUE NOBODY NAMED, and reading it as style would have left the
census itself nameless.

⚑ NOTHING DOWNSTREAM CHANGES. Twenty `set_ratchet` call sites and thirty-eight
`check_argv` call sites across twenty-two files — including
`jea/metalanguage/sorted_stream.py`, outside `scripts/` — keep importing from here with
their existing signatures.
"""

from __future__ import annotations

import sys

from mikemol.hooks.refusal_log import Refusal, stream_tool
from mikemol.ratchet.render import Report

from scripts.ratchet_legacy import set_ratchet
from substrate.baseline_io import may_write, read_baseline, split_moves, write_baseline
from substrate.baseline_state import BaselineState
from substrate.proc_ancestry import ancestry, check_cycle, is_interpreter_wrapper
from substrate.ratchet_core import Census, Permission, partition
from substrate.ratchet_flags import (
    TENANT_FLAGS,
    UNIVERSAL_FLAGS,
    check_argv,
    mutating_argv,
    store_argv,
)
from substrate.ratchet_suites import run_all
from substrate.vlogs_destination import log_fallthrough
from substrate.withheld_verdict import withheld

# ⚑⚑ THE ISLAND MOVED TO `substrate/` (⟡gate-island-promote) AND NOTHING DOWNSTREAM CHANGED —
# which is the whole reason this facade was worth keeping. Twenty `set_ratchet` call sites and
# thirty-eight `check_argv` call sites across twenty-two files import from HERE; a facade of
# pure re-exports means a promotion is one edit to these lines rather than sixty edits to
# files that are mostly too dirty to edit at all.
#
# ⚑ `ratchet_legacy` STAYED BEHIND, DELIBERATELY. It is the twelve-argument adapter for the
# unmigrated call sites, and its `pyproject.toml` exemption exists to be DELETED when they
# move to `Census.of`. Copying it to `substrate/` would have duplicated an exemption whose
# purpose is to disappear — extending debt in the act of promoting.
#
# ⚑ `vlogs_url` WAS DROPPED (W38c): mtools' `refusal_log` reads no environment and takes its
# destination as an argument, which `vlogs_destination` resolves by name. Censused first: no
# consumer here or in el-openglo (whose copies are symlinks of this file) calls it.

# ⚑ RE-EXPORTED DELIBERATELY, NOT INCIDENTALLY. Every name here has live consumers that
# import it FROM `ratchet` — `check_argv` alone has 38 call sites across 22 files, one of
# them outside `scripts/`. Declaring the surface is what makes this file's job explicit
# rather than leaving a linter to read the imports as unused.
__all__ = [
    "TENANT_FLAGS",
    "UNIVERSAL_FLAGS",
    "BaselineState",
    "Census",
    "Permission",
    "Refusal",
    "Report",
    "ancestry",
    "check_argv",
    "check_cycle",
    "is_interpreter_wrapper",
    "log_fallthrough",
    "may_write",
    "mutating_argv",
    "partition",
    "read_baseline",
    "run_all",
    "set_ratchet",
    "split_moves",
    "store_argv",
    "stream_tool",
    "withheld",
    "write_baseline",
]


if __name__ == "__main__":
    if "--selftest" in sys.argv:
        raise SystemExit(run_all())
    sys.stdout.write(f"{__doc__}\n")
    raise SystemExit(2)
