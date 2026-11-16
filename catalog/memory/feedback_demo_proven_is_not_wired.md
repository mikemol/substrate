---
name: feedback_demo_proven_is_not_wired
description: "a property proven inside a module's __main__ DEMO is not \"done\" -- it is orphaned until something IMPORTS and composes it; mechanical test = grep for importers, and check the real consumer doesn't fake the input"
metadata: 
  node_type: memory
  type: feedback
  originSessionId: c1329ff9-896f-4600-8952-67ec237e5bbc
---

A capability demonstrated in a script's `if __name__ == "__main__":` block is NOT done. It is
**orphaned** until another module IMPORTS it and the real running system COMPOSES it. "It passes
its demo" ≠ "it is wired." (User, 2026-06-16, jea: I had marked the live-control loop done because
each piece's demo PASSed; an import audit showed jea_navigator / jea_telemetry / jea_actuator /
jea_megakernel were imported by NOBODY, and the apex's __main__ HAND-PUBLISHED its schedule from a
hardcoded list instead of calling navigate(collect_package()) -- the reactive loop drove nothing.)

**Why:** demos let you prove a property in isolation and then move on, leaving the integration
undone; the system keeps running on a FAKE stand-in input (a hardcoded list, a representative DAG)
that LOOKS like the real wiring. This is [[feedback_silo_sprawl_orphans_fixes]] (orphaned work) +
[[feedback_validate_outputs_not_inputs]] (the demo validates the piece, not the composition) made
mechanical.

**How to apply (the import-audit, run it before claiming any multi-module arc "complete"):**
1. For each module M that's supposedly part of the running system: `grep -lE "import M|from M " *.py`.
   If only M's own file matches -> M is a STANDALONE DEMO, orphaned. Its property feeds nothing.
2. Find the real consumer (the thing actually launched) and check it does NOT fake the input: a
   hardcoded list, a `representative` sample, a hand-picked constant where the live solve should be
   is the tell that the producer is orphaned and the demo's reactivity is theatre.
3. "Done" requires an IMPORT EDGE from the running system to the module AND the fake stand-in
   DELETED. Acceptance criteria should name that edge, not "the demo PASSes".
Related orchestration corollary: do not leave a DECISION (operating point / dispatch / select) on
the host as "orchestration"; if a device-resident supervisor can read uploaded telemetry and decide,
the host-side decision is the orphan/host-sync to remove (recompute-from-residue on-device).
