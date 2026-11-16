#!/usr/bin/env python3
# SPDX-License-Identifier:Apache-2.0
# Copyright 2026 Mike Mol
"""⚑ SCAFFOLD — measures what `T28-closure`'s boolean cannot say.

`worklist_gate` filters `rests-on` with `if d in bib`, so a grounding edge whose
target exists in NO bib is DROPPED rather than reported.  The engine's
`bib.rests_closure` returns `(reachable, dangling)` precisely so that edge
surfaces.  T28-closure's size is `len(gaps)` over a two-branch decision tree, so
it can only ever report 0 or 1 — a boolean wearing an integer, which is why the
item ranked as "size 1" beside a 42-module class.

This prints the population the item would actually move.  Delete once the
measurement lives in the witness.
"""
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PROJECT = os.path.join(ROOT, "catalog", "worklist")
sys.path.insert(0, os.path.join(ROOT, "scripts"))

import worklist_gate as W  # noqa: E402

root, why = W.engine()
if root is None:
    print("cannot reach engine: %s" % why)
    sys.exit(2)
sys.path.insert(0, root)
import paperkit.bib as B  # noqa: E402

bib = B.parse(os.path.join(PROJECT, "warrants.bib"))
authored = dict(bib)
derived = W.derived_failures()
bib.update(derived)

for label, F in (("authored only", authored), ("authored + derived", bib)):
    reach, dang = B.rests_closure(set(F), F)
    print("%-20s  %d key(s), %d reachable, %d DANGLING"
          % (label, len(F), len(reach), len(dang)))
    for c, t in sorted(dang):
        print("     %s -rests-on-> %s   (target in no bib)" % (c, t))
