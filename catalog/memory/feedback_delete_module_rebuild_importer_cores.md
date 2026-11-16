---
name: feedback_delete_module_rebuild_importer_cores
description: "deleting an Agda module → a stale TRANSITIVE-importer .agdai reads UNDECODABLE and the set1-ratchet's incomplete-census guard aborts the commit; run `make -C agda -j` to rebuild ALL importer cores before re-committing, not just rm the deleted module's own orphan"
metadata:
  type: feedback
  originSessionId: d35bc15a-16b8-42c5-aad1-20966c9a9f8e
---

When you DELETE an Agda module (e.g. `Conway/Distrib.agda`), rm-ing its OWN orphan
`_build/.../X.agdai` is NOT enough. Any module that TRANSITIVELY imported it — an
aggregator/`Manifest` that bare-imports a chain reaching the deleted module — keeps a
stale `.agdai` whose interface chain is now broken; the set1-ratchet's core reader
(`decode_core`) reports it **UNDECODABLE** and the gate aborts:
`set1-ratchet(cores): N of M cores UNDECODABLE — census incomplete … Rebuild cores; do
not certify.` (Correct guard — an incomplete census is not a low count.)

**Why:** isolate-checks (`membudget run … agda … <file>`) only rebuild the files you
NAME, so directly-edited consumers get fresh cores but untouched transitive importers
do not; `full_build_check.py` builds agda directly and may not repopulate the make-style
`_build` cores the ratchet reads.

**How to apply:** after ANY module deletion, before the gated commit, run
`make -C agda -j` (the shim/membudget-routed path that repopulates ALL stale `_build`
cores in dependency order) — then the ratchet reads a complete census. Confirmed live
2026-07-17: deleting `Conway/Distrib.agda` left `Conway/Manifest.agdai` undecodable →
the rc-conway commit aborted → `make -j` rebuilt Manifest fresh → re-commit landed
census 0. Widens the standing "rm orphan .agdai before measuring" note (that covers the
deleted module's OWN orphan; this covers its IMPORTERS'). Relates to
[[set1-census-artifact-class]].
