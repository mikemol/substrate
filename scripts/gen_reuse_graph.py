#!/usr/bin/env python3
# gen_reuse_graph.py — regenerate the structure REFINEMENT/REFERENCE graph: nodes = data/record
# structures, edge X -> Y iff X's elaborated core REFERENCES Y (Y is a component/parent X is built
# on). Extracted from the RAW agdai_shim cores, whose nodes carry qname references
# (constructor/qname/children) — the interned form drops them. Complements the flat reuse-index
# (name->home) + its parallel-detector with the EDGE layer (DivStr <- GradedDivStr <- …), and
# yields the "highly-reused primitive vs never-refined" degree ranking.
#
# The reducer + the .agdai decode phase now live in scripts/reuse_catalog.py (SHARED with
# gen_reuse_index.py — one shim-walk, two reducers; see that module's header). This is the thin
# single-catalog entry point: it drives ONLY the graph reducer. To regenerate BOTH catalogs from a
# single decode pass (the gate path), use scripts/gen_catalog.py.
#
# Emits, in formats the LLM-consumer is fluent in (trained-on) + that have tooling:
#   catalog/reuse-graph.dot — every structure->structure edge (GraphViz; queryable/renderable).
#   catalog/reuse-graph.md  — a Mermaid slice of the top reuse-primitives + their refiners,
#                             plus the in/out-degree ranking.
# Regenerate: scripts/gen_reuse_graph.py [path-substring-filter]  (~3min full; runs the shim raw).
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from reuse_catalog import generate          # noqa: E402

if __name__ == "__main__":
    filt = sys.argv[1] if len(sys.argv) > 1 else ""
    for m in generate(filt, do_index=False, do_graph=True):
        print(m)
