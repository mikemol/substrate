#!/usr/bin/env python3
# gen_reuse_index.py — regenerate catalog/reuse-index.md, the substrate's REUSE GUARD: a name ->
# canonical-home index of every data/record STRUCTURE, so a re-implementer (LLM or human) can look
# up "does X already exist, and where" BEFORE re-deriving it. The discoverability fix for the class
# of re-implementations the z47 arc surfaced (a Klein four-group already in Groups.V4, a
# continued-fraction real already in Algebra.R.Trace, a wedge already in Algebra.Wedge, …).
#
# The reducer + the .agdai decode phase now live in scripts/reuse_catalog.py (SHARED with
# gen_reuse_graph.py — one shim-walk, two reducers; see that module's header). This is the thin
# single-catalog entry point: it drives ONLY the index reducer. To regenerate BOTH catalogs from a
# single decode pass (the gate path), use scripts/gen_catalog.py.
#
# Consume: grep catalog/reuse-index.md for your concept (V4 / Real / Wedge / Monoid / Stream /
# Trace / DivStr / …). Regenerate: scripts/gen_reuse_index.py (idempotent, ~2min).
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from reuse_catalog import generate          # noqa: E402

if __name__ == "__main__":
    filt = sys.argv[1] if len(sys.argv) > 1 else ""
    for m in generate(filt, do_index=True, do_graph=False):
        print(m)
