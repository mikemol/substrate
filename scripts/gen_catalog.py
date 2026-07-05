#!/usr/bin/env python3
# gen_catalog.py — regenerate BOTH discoverability catalogs from a SINGLE `.agdai` decode pass.
#
# The two catalogs — catalog/reuse-index.md (name -> canonical-home + cross-name shape-parallels)
# and catalog/reuse-graph.{dot,md} (structure -> structure refinement edges + reuse-primitive
# degree census) — are derived from the SAME shim-walk over the typechecked cores; they diverge
# only in the reducer (scripts/reuse_catalog.py). Running the two standalone generators
# back-to-back decodes the whole tree TWICE (~1751 files × 2). This entry point runs the shared
# walk ONCE and drives both reducers off it — halving the combined cost. It is the GATE path: the
# pre-commit hook calls this after the forced full build so both catalogs regenerate together and
# neither rots behind a structural change.
#
# Regenerate by hand: scripts/gen_catalog.py [path-substring-filter]  (~2-3min full).
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from reuse_catalog import generate          # noqa: E402

if __name__ == "__main__":
    filt = sys.argv[1] if len(sys.argv) > 1 else ""
    for m in generate(filt, do_index=True, do_graph=True):
        print(m)
