#!/usr/bin/env python3
# SPDX-License-Identifier:Apache-2.0
# Copyright 2026 Mike Mol
"""Remove an `opaque` wrapper from named defs (the inverse of seal_defs.py).

⚑ SEAL THE PROOF, NEVER THE NEUTRAL THE PROOF IS ABOUT.  A blanket seal over a
Laws part also catches its FUNCTIONS (`basis`, `sum`, `convCoeff`, `x-power`, …),
whose definitional unfolding consumers need — the `_*Q_` failure mode.  This
un-wraps exactly those, dedenting the block back to the telescope indent.

USAGE: unseal_defs.py <file.agda> <name> [<name> …] --apply
"""

import re
import sys
from pathlib import Path

# ⚑⚑ `_snapshot_once` WAS DELETED HERE (Ⓐ49 ⟡split-8-unprotected), not moved.  Its
# rationale is KEPT AS RESIDUE below, because it was RIGHT about the danger and only
# wrong about the PLACEMENT:
#
#   "This tool rewrites files it read — the shape that made 33 files unrecoverable
#    (Coxeter/Core.agda 76 lines -> 3).  The write is inside a loop, so a per-file
#    `guard` would arm only the first file AND shell out to `git stash create` on
#    every iteration; arming once per run is both correct and cheap."
#
# "Arm once per run" is now satisfied STRUCTURALLY rather than by a `_SNAPPED`
# sentinel: the snapshot rides the single entry-point intent statement, which happens
# exactly once per run by construction.  The sentinel existed only to make a WRITE-SITE
# call idempotent, and the write-site call IS the defect — it fires after every decision
# has been made, so a run that unsealed nothing took no snapshot at all.
#
# ⚑ AND LEAVING IT AS DEAD CODE MADE THE CENSUS READ FALSE-RED.  `pycodemod
# --unbound-snapshot` keys on a `guard` CALL SITE being present in the file, not on that
# site being REACHABLE — so with the binding done and this helper still defined,
# `--calls _snapshot_once` reported `1 def, 0 calls` while the tool still classified
# SPLIT.  That is the exact MIRROR of the false GREEN this arc exists to close: both are
# the census reading SOURCE POSITION where the question is about EXECUTION.
# ⚑⚑ INTENT AT ENTRY (Ⓐ44 ⟡move-guards-to-entry).  This file has NO `__main__` block —
# the script body IS the entry point — and no dry-run path: the `open(path,"w")` below
# runs unconditionally.  Placed at the top of the script body.
# ⚑ AND THE OPERANDS ARE THE NAME SET, so a mutation flag must be filtered out of them
# or `--apply` would be read as a definition to unseal.
# ⚑⚑⚑ SNAPSHOT BOUND TO THE INTENT STATEMENT (Ⓐ49 ⟡split-8-unprotected).  The intent
# check moved here under Ⓐ44 while `_snapshot_once` stayed at the write — so this tool
# read COMPLIANT to `intent_census` and was UNPROTECTED for any run that decided not to
# write.  `require_at_entry(paths=...)` delegates to `guard` past the intent check, so
# stating `--apply` IS taking the snapshot: one act, one placement, no second site.
# ⚑ `paths` IS NOT MERELY ADVISORY HERE.  `snapshot()` is whole-worktree for TRACKED
# content, but `_copy_untracked(paths)` is the ONLY protection for UNTRACKED files —
# which is the population most likely to need recovering.  So the target is resolved
# from argv BEFORE the entry call, and the operand filter is hoisted with it.
import edit_snapshot as _es

_argv = [a for a in sys.argv[1:] if not a.startswith("--")]
_es.require_at_entry("unseal_defs", paths=_argv[:1])
if "--dry-run" in sys.argv:
    _msg = (
        "unseal_defs has NO dry-run path: the rewrite is unconditional.\n"
        "  Refusing rather than writing under a stated --dry-run.\n"
        "  successor:  unseal_defs.py <file.agda> <name>... --apply"
    )
    raise SystemExit(_msg)
# ⚑ `_argv` was destructured ABOVE, at the entry call, because the snapshot needs the
# target path.  Re-splitting it here would be a second reading of argv that can drift.
path, names = _argv[0], set(_argv[1:])
with Path(path).open(encoding="utf-8") as f:
    L = f.read().split("\n")
out, i, done = [], 0, []
while i < len(L):
    m = re.match(r"^(\s*)opaque\s*$", L[i])
    if m:
        ind = len(m.group(1))
        j, blk = i + 1, []
        while j < len(L) and (not L[j].strip() or len(L[j]) - len(L[j].lstrip()) > ind):
            blk.append(L[j])
            j += 1
        sig = next((b for b in blk if b.strip()), "")
        nm = re.match(r"^\s*([^\s{}()]+)\s*:(?!:)", sig)
        if nm and nm.group(1) in names:
            out += [(b.removeprefix("  ")) for b in blk]
            done.append(nm.group(1))
            i = j
            continue
    out.append(L[i])
    i += 1
# ⚑ THE WRITE-SITE SNAPSHOT IS GONE, NOT MOVED (Ⓐ49).  It fired here, after every
# decision had been made, which is why a run that changed nothing went unprotected.
# The snapshot is taken at the intent statement above, on the same argv-derived path.
with Path(path).open("w", encoding="utf-8") as f:
    f.write("\n".join(out))
sys.stdout.write(f"unsealed in {path}: {', '.join(done) or '(none)'}\n")
