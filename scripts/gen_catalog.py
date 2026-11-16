#!/usr/bin/env python3
# SPDX-License-Identifier:Apache-2.0
# Copyright 2026 Mike Mol
# gen_catalog.py — regenerate ALL discoverability catalogs from a SINGLE `.agdai` decode pass.
#
# ONE expensive walk builds catalog/catalog.db (the canonical relational store); every artifact is
# then a fast RENDER over it (scripts/reuse_catalog.py). This entry point builds the DB once and
# renders all of:
#   catalog/reuse-index.md        — name -> canonical-home + cross-name shape-parallels
#   catalog/reuse-graph.{dot,md}  — STRUCT refinement edges + reuse-primitive degree census
#   catalog/reuse-sitemap.xml     — flat discovery manifest (priority = in-degree); the LLM-fluent format
#   catalog/usage-stats.md        — reuse distribution: real primitives vs structurally-isolated
#   catalog/import-graph.{dot,md} — MODULE semantic-dependency edges (over the cores, not source imports)
# It is the GATE path: the pre-commit hook calls this after the forced full build so every catalog
# regenerates together and none rots behind a structural change. catalog.db itself is a derived
# local cache (gitignored, non-deterministic binary); the gate stages only the committed renders.
#
"""USAGE

gen_catalog.py [path-substring-filter]   # the FULL path: one `.agdai` decode walk builds
                                         # catalog.db, then every artifact above renders
                                         # off it (~2-3 min for the whole corpus).
gen_catalog.py --render-only             # RE-RENDER ONLY — reuse the existing catalog.db
                                         # and skip the decode walk entirely. The fast loop
                                         # when a RENDERER changed and the cores did not.
                                         # ⚑ It reads whatever catalog.db already holds, so
                                         # a stale DB renders stale catalogs silently; use
                                         # the full path after any change to the tree.
⚑ THESE TWO LINES WERE `#` PROSE UNTIL THE DIVERGENCE CENSUS READ `--render-only` AS
UNDECLARED. They said the right thing in the wrong shape: `parse_usage` keys on a line
naming the tool, and inside a run of `#` comment lines this one was absorbed as the
CONTINUATION GLOSS of the line above rather than read as a usage line of its own. A
docstring is the shape every other tool here uses and the shape the parser reads.
"""

import os, sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from reuse_catalog import generate  # noqa: E402

if __name__ == "__main__":
    argv = sys.argv[1:]
    reuse_db = "--render-only" in argv
    rest = [a for a in argv if a != "--render-only"]
    filt = rest[0] if rest else ""
    for m in generate(filt, reuse_db=reuse_db):
        print(m)
