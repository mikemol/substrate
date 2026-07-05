#!/usr/bin/env python3
# gen_catalog.py — regenerate ALL discoverability catalogs from a SINGLE `.agdai` decode pass.
#
# ONE expensive walk builds catalog/catalog.db (the canonical relational store); every artifact is
# then a fast RENDER over it (scripts/reuse_catalog.py). This entry point builds the DB once and
# renders all of:
#   catalog/reuse-index.md        — name -> canonical-home + cross-name shape-parallels
#   catalog/reuse-graph.{dot,md}  — structure refinement edges + reuse-primitive degree census
#   catalog/reuse-sitemap.xml     — flat discovery manifest (priority = in-degree); the LLM-fluent format
#   catalog/usage-stats.md        — reuse distribution: real primitives vs structurally-isolated
# It is the GATE path: the pre-commit hook calls this after the forced full build so every catalog
# regenerates together and none rots behind a structural change. catalog.db itself is a derived
# local cache (gitignored, non-deterministic binary); the gate stages only the committed renders.
#
# Regenerate by hand: scripts/gen_catalog.py [path-substring-filter]  (~2-3min full).
# Fast re-render from an existing DB (no walk): scripts/gen_catalog.py --render-only
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from reuse_catalog import generate          # noqa: E402

if __name__ == "__main__":
    argv = sys.argv[1:]
    reuse_db = "--render-only" in argv
    rest = [a for a in argv if a != "--render-only"]
    filt = rest[0] if rest else ""
    for m in generate(filt, reuse_db=reuse_db):
        print(m)
