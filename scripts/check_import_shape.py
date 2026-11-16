#!/usr/bin/env python3
# SPDX-License-Identifier:Apache-2.0
# Copyright 2026 Mike Mol
"""check_import_shape.py — enforce shape-specialized imports of colliding names.

Names are vacuous; a name declared in >1 module with DIFFERENT shapes must be
specialized at import — `open import M using () renaming (Name to Name⟦shape⟧)`
or qualified — never brought in bare, so the reader sees which shape. This
flags modules that `using (Name)` a genuinely-ambiguous Name without renaming
it. Excludes level-polymorphic foundation dups (⊤/⊥ — same object, lifted).

Usage: check_import_shape.py [--quiet]   (exit 1 on violations.)
"""

import os, re, sys, collections

# ⚑⚑ THE SHAPE COMPUTATION IS NOT LOCAL ANY MORE, AND IT NEVER SHOULD HAVE BEEN.
# This file walked the tree and hashed declarations itself; `sppf_node_index.py`
# did the same, byte-identically — and the two DISAGREED, because `ALLOW` lived
# only here and the module-count test lived only there.  MEASURED 2026-08-18:
# this gate reported **9** genuinely-ambiguous names while the index it cites in
# its own failure message published **11** — the difference being exactly `⊤` and
# `⊥`, the level-poly dups this file exempted and the index did not.
#
# ⚑ SO AN OPERATOR FOLLOWING THE REMEDY WAS SENT TO AN INDEX THAT DISAGREES WITH
# THE GATE THAT SENT THEM.  This is the same lesson `_rename_pairs` taught two
# lines below — a private copy of a shared relation — for the relation the parser
# is used to compute.  One authority: `_agdatext.shape_decls` + `genuine_ambiguity`.
import _agdatext

sys.path.insert(
    0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "scratch")
)
from scope_fix import _rename_pairs  # THE renaming-clause parser; never re-derive

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "agda", "Substrate"))
genuine = _agdatext.genuine_ambiguity(_agdatext.shape_decls(ROOT), _agdatext.LEVEL_POLY_DUPS)
# the import scan still needs the stripped source of every module
texts = {}
for dp, _, fns in os.walk(ROOT):
    for fn in fns:
        if fn.endswith(".agda"):
            p = os.path.join(dp, fn)
            texts[p] = _agdatext.strip(open(p, encoding="utf-8").read())

# scan imports: a `using (...)` naming a genuine name without `renaming (Name to`
imp = re.compile(r"open\s+import\s+\S+([^\n]*(?:\n\s+[^\n]*)*)")  # stmt + continuations
viol = collections.defaultdict(list)
for p, t in texts.items():
    for m in imp.finditer(t):
        clause = m.group(1)
        us = re.search(r"using\s*\(([^)]*)\)", clause, re.S)
        if not us:
            continue
        names = set(w for w in re.split(r"[\s;,]+", us.group(1)) if w)
        # ⚑ THIS WAS A NON-GREEDY COPY THAT SAW ONLY THE FIRST PAIR.
        # `renaming\s*\([^)]*?(\S+)\s+to\s` stops at the first ` to `, so a
        # multi-pair clause `renaming (a to x; b to y)` yielded {a} and dropped b.
        # MEASURED by the DRY audit: 52 statements / 48 distinct source-names
        # invisible (`_*_`, `+-assoc`, `_≤_`, `sbox-rt`, `outer`, `anti-diag-sum`).
        # Purely false-negative, and today's verdict is unchanged (0 -> 0) — but with
        # BASELINE = 0 and the policy "enforced for new code today", the FIRST new
        # multi-pair import of a genuinely-ambiguous name would pass this gate
        # SILENTLY.  A gate that cannot see half its input will be wrong the first
        # time it matters, and it is a PRE-COMMIT gate.
        # `scope_fix._rename_pairs` is THE parser (drop_dead_renames, demand_imports,
        # rewire_to_leaves); this is the fourth adopter.
        ren = {src_name for src_name, _tgt in _rename_pairs(clause)}
        for n in names & genuine:
            if n not in ren:
                viol[n].append(os.path.relpath(p, ROOT))

# RATCHET: a large codebase can't retrofit 90 sites at once. Gate on NO NEW
# bare colliding imports (count may only go down). Lower BASELINE as they're
# fixed; the policy is enforced for new code today.
# 2026-06-26: baseline RETIRED — all grandfathered bare colliding imports specialized
# (Bool deduped; every Wedge import shape-pinned, migrated + baseline). Now ZERO by construction.
BASELINE = 0
n = sum(len(v) for v in viol.values())
over = n > BASELINE
if "--quiet" not in sys.argv or over:
    print(
        f"import-shape: {len(genuine)} genuinely-ambiguous names; "
        f"{n} bare imports (baseline {BASELINE}).",
        file=sys.stderr if over else sys.stdout,
    )
    if "--quiet" not in sys.argv:
        for nm, files in sorted(viol.items(), key=lambda kv: -len(kv[1])):
            print(f"  {nm}: {len(files)}  ({', '.join(files[:4])}{' …' if len(files) > 4 else ''})")
    if over:
        print(
            f"  GATE FAILED: {n} > {BASELINE} — a NEW bare colliding import. Specialize "
            f"by shape: `renaming (Name to Name⟦shape⟧)` (see scratch/sppf_collision_index.md).",
            file=sys.stderr,
        )
    elif n < BASELINE:
        print(f"  (note: {n} < baseline {BASELINE} — lower BASELINE in check_import_shape.py.)")
sys.exit(1 if over else 0)
