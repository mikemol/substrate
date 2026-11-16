---
name: record-versioning-is-differential-measurement
description: "a per-record version exists to make before/after READABLE, not merely to detect staleness; without it every repair is verified by re-running a whole-population scalar"
metadata: 
  node_type: memory
  type: project
  originSessionId: d35bc15a-16b8-42c5-aad1-20966c9a9f8e
  modified: 2026-08-03T14:06:03.907Z
---

**Why record versioning is the arc** (user, 2026-08-03: *"It's needed because otherwise,
there's no way to tell the difference of a before/after."*).

I justified it as DETECTION — tombstones for orphan cores, cheaper completeness guards.
That is the weaker reading. The load-bearing reason is **differential measurement**: with
no per-record version, a repair can only be verified by re-running a full measurement and
comparing TOTALS. That is a scalar over a whole population — the cleaver
[[realizability-charter]] names, not the differential. A version makes the delta readable
PER RECORD.

It explains a recurring shape rather than one defect: `--discriminates` returning 0 with no
mutator applied; `dagcone.orient` reporting `0 oriented / 0 free / 2 conflict`; "48% failure"
and "12% defect rate" being the same run read two ways. Each was an instrument that could
report a STATE but not a CHANGE.

**Measured 2026-08-03**, substrate: `core_fp(core_id, mtime)` versions a FILE (its own
`.agdai` mtime, `scripts/sppf_db.py:123-127`). A record's validity depends on a
NEIGHBOURHOOD — its source, its own bytes, its dependencies' versions — so:
- ~1148 of 3131 cores (~37%) do not decode; unchanged across a fresh full build, so this is
  the live state, not stale residue
- 85 cores have no `.agda` at all; 50 of those hold a LIVE `core_fp` row and contribute
  796 `unit_obs` / 65873 `edge` / 796 `_unit` rows describing retired modules
- every guard built to catch this reads the FILESYSTEM to answer what the RECORD should carry

Shape the numbers support: fold RECORDED dep versions at **depth 1**, never recompute the
closure (`Foundation/Level`'s reverse closure is 3196 of 3456 = 92.5%, but median fan-in is
2 — recomputation is the pathology, not the fold). Agda already supplies the primitive:
`iImportedModules :: Interface -> [(TopLevelModuleName, Hash)]` — a content hash per import,
which IS the recorded dep version. Verified reachable at `jea/metalanguage/agdai_shim.hs:196`
where the decoded `Interface` is held; absent from the import list at `:39-41`.

Related: [[feedback_report_presence_never_absence]], [[cost-is-structural-times-live]].
