# Event-sourcing rebuild — plan + status

**Directive (2026-07-12):** "sppf_db is an append-only writer. The SPPF is the intermediate projection.
The catalog and every other current table becomes a query against the SPPF projection."

## The layering (dependency order)
1. **EVENTS** (append-only source of truth) — `sppf_db` writes them. An event = `base64(one raw
   OBSERVATION)` = the decoded node exactly as the shim emits it: `{constructor, qname, index,
   children:[LOCAL ids]}`. Bounded by construction (one node's data, children as flat local ids, NO
   resolution). Measured: max 312 chars over 60 cores — vs the entire-record/Merkle version's 194 368 on
   2 cores. The blowup came from base64-ing the POST-PROCESSED record (children resolved to subtree
   content-addresses); event sourcing records the observation, not its post-processing.
2. **SPPF projection** (intermediate, DERIVED from events) — the packing SPPF (`_node`/`node_child`/
   `unit_node`) computed by query over `event`/`obs`/`edge`. This is where global structural sharing /
   canonicalization happens (per-core local refs resolved, folded into global packing ids).
3. **Catalog + all else** (DERIVED from the SPPF projection) — reuse_catalog's structs/refs/members and
   the readouts become queries against the projection.

## Event schema (source of truth)
- `event(ekey PK, ctor_id, qname_pid, idx)` — distinct raw observations; ctor/qname interned (base64 terms/path).
- `obs(core_id, local_id, ekey)` — each core's decoded node → its event (UNIQUE core_id,local_id).
- `edge(core_id, plid, ord, clid)` — raw local parent→child edges as observed.
- `unit_obs(core_id, unit_pid, root_lid, kind_id)` — from defmarks.
- terms/path_seg shared (base64, content-addressed).

## SPPF projection (derived — must reproduce current numbers)
head per event (matches jea_agdai.go): kind=AgdaCore; Var/PVar→role=`db{idx}`; FREE+qname→op=qname;
else→op=ctor. symbol=base64(head). packing=base64(head ‖ [child symbols ordered]) — a 1-JOIN (symbol is
head-only, not recursive). `_node`=distinct packings; `node_child`=(parent_packing,ord,child_packing);
`unit_node`=per-unit membership reachable from root over raw `edge` (acyclic).
ACCEPTANCE: Category subset must reproduce 14 913 packings / 2 793 symbols / support median 15;
full tree 76 629 packings, node_id max 4184.

## Phases
- [x] **P1** event writer (`write_events`) — decode → event/obs/edge/unit_obs, append-only, txn/file.
      DONE: 43 586 events / 124 949 obs, **max ekey 312 (bounded)**. Category subset.
- [x] **P2** SPPF projection (`project_sppf`) reading events → `_node`/`node_child`/`unit_node`.
      DONE: reproduces **14 913 packings / 2 793 symbols / max id 1244 / support median 15** exactly;
      sppf_query support/clusters/extract identical (named-Functor=18). Fixed: file_id must be interned
      (unit view inner-join). KNOWN tiny delta: unit_node 66 459 vs 66 436 (+23, ~0.03%) — real queries
      identical; verify later → `⟡es-unitnode-delta`.
- [ ] **P3** catalog as queries against the SPPF projection (reuse_catalog re-derivation). Bigger; reuse-index.md byte-identical is the gate.
- Follow-up: SQL-native projection (UDF base64) so P2 is a pure query, not a Python fold — `⟡sppf-projection-sql`.
