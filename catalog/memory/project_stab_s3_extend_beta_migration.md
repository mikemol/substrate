---
name: project_stab_s3_extend_beta_migration
description: Stab-S3-Extend round-trips migrated from 72 with-in clauses to β-laws; alloc 933→531 MB (−43%); first validated instance of the OOM lever
metadata: 
  node_type: memory
  type: project
  originSessionId: b0f173b0-7c01-42e2-bd3c-cbed23f2d66a
---

First applied instance of the β-law-over-enumeration lever identified in
[[project_oom_memory_profile_2026_06]] (case-COUNT, not data size, drives
checking cost). Target was the measured allocation hog `Stab-S3-Extend`
(933.4 MB).

**What changed** (`agda/Substrate/Groups/Stab-S3-Extend.agda`):
`extend-inv-l` / `extend-inv-r` were 72 `with ... in p`-captured clauses
(4 anchor × 4 axis × 3 Fin dispatch) calling inv-l-helper/inv-r-helper.
Replaced with:
- `extend-fn-β` : extend-fn anchor g (fin3-to-non-anchor anchor i) ≡
  fin3-to-non-anchor anchor (g i) — the commute-with-forward-bridge
  β-law, proved by axis-cover × fin-cover = 12 refls (each anchor×pos
  reduces, fin3-to-non-anchor anchor <lit> is a concrete lookup).
- `off-l`/`off-r` : ONE off-diagonal kernel each (β-law + SFin.inv-l/-r).
- `extend-inv-l`/`-r` : 16 one-line clauses each (4 diag refl + 12 kernel
  calls). NO `with` — the construct that drove the allocation.

`extend-fn` (the 16-case table consumers reduce through) was left
UNTOUCHED, so consumer reduction behaviour is identical.

**Results (measured):** alloc 933.4 → 531.5 MB (−402 MB, −43%); .agdai
99.7 → 72.9 KB (−27%); 294 → 253 lines; with-in clauses 24 → 0;
postulates 0. All 5 consumers green (Stab-S3-Hom, -Iso, S4Iso-Bridges,
S4Iso/Anchor, S4Iso/StabElements) — they import `extend` /
`extend-apply-pointwise-cong`; the rewritten round-trips are only the
inv-l/inv-r record FIELDS, whose type is unchanged, so consumers that use
`extend`'s type (not its inv proofs' reduction) are unaffected.

**Why this one was safe** (vs the reverted Stab-S3 bridge attempt in
[[project_punctured_fin_primitive]]): the rewritten functions are PROOFS
consumed only by type, and the consumer-facing `extend-fn` reduction was
preserved. The earlier failure changed a function whose REDUCTION
consumers banked. Rule of thumb: rewrite proof bodies freely; preserve
definitional reduction of anything consumers compute through.

**Remaining headroom:** 531 MB still includes the 387 MB framework-load
floor, so intrinsic is ~145 MB (down from ~546). The 16-clause enumerations
(extend-fn, extend-apply-pointwise-cong) could go fully parametric via the
Fin.Punctured.Pointed `extend`/β-laws, but that touches extend-fn's
reduction → consumer risk → its own measured slice. Next candidates by the
profile: V4-Coxeter (148 KB), Z3-Coxeter (103 KB). See
[[feedback_common_substructure_recursively]].
