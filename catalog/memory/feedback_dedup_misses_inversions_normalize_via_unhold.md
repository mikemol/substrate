---
name: feedback_dedup_misses_inversions_normalize_via_unhold
description: "The SPPF dedup (jea_pysim) matches SHARED interned structure, so it CANNOT detect a redundancy that is an INVERSION — same concept, dual representation (grade-collapse vs grade-index, hold-as-field vs index-by-parameter). The fix: cluster MODULO the reconstruct `un-hold` repair (held carrier → grade-index parameter) as a pre-interning normalization, then shared-subtree matching catches inversions. repair is also a normalizer, not only an emitter."
metadata:
  node_type: memory
  type: feedback
  originSessionId: d35bc15a-16b8-42c5-aad1-20966c9a9f8e
---

Caught 2026-07-11 (⟡upfamily-rewire). I recognized BY HAND that `UniversalProperty.ArrowOfArrow
.UPArrow²` (record : Set₂, holds two UPArrow fields + a UPMorphism) is the rig cat INVERTED — it
HOLDS the tower levels as fields (climbing the universe tower L0:Set₁→L2:Set₂→L3:Set₃) where the rig
cat INDEXES by the ℕ-grade (Obj : ℕ → Set, Set₀), so `ι : UPArrow² → UPArrow` IS the grade-collapse.
The user asked: *"why didn't our deduplication machinery / pipeline detect this, rather than drive us
to start rebuilding it?"* Measured it: `jea_pysim --clusters` over ArrowOfArrow + OrientationRigCat +
OrientationBifunctor puts UPArrow² and the rig cat in SEPARATE clusters (73.8% partial) — cluster 0 =
UPArrow²'s own L0-Source/L0-Target, cluster 1 = the rig cat's ⊕obj/⊗obj. No cross-match.

**Why (root cause):** jea_pysim's dedup keys on SHARED interned subtrees (SPPF fan-in = corroborated
shape). UPArrow²↔rig-cat is not shared shape — it is an INVERSION: `holds a level as a FIELD`
(`L0-Source : UPArrow`) vs `indexes by a grade PARAMETER` (`Obj : ℕ → Set`) intern to STRUCTURALLY
DIFFERENT nodes. The very move that makes UPArrow² redundant (grade-collapse = the dual of the rig
cat's grade-index parameterization) is exactly what makes their terms structurally distinct, so
shared-subtree matching is blind to it BY CONSTRUCTION. The census `locate` (set1_locate_census.py)
DID flag UPArrow² — as `holds-set1-field`, "reducible-transitively, recurse on UPArrow" — but that is
"it's a Set₁-ish defect," NOT "this already exists as the rig cat, route don't rebuild." Detecting
redundancy-under-inversion is a DIFFERENT capability than detecting a defect or same-shape duplicate.

**How to apply (the fix — ⟡dedup-unhold-normalizer, jea_pysim `--unhold`, committed).** The bridging
transformation is the `reconstruct` `un-hold` (held carrier/level field → grade-index parameter).
Wired as a pre-interning normalization: `jea_pysim --unhold` interns every carrier reference (Record/
Datatype qname, `Sort`, `ℕ→Set`) to the shared canonical `⟨CARRIER⟩` node (jea_agdai.intern_signature
`carrier_qnames`), so a record that HOLDS a carrier and one that INDEXES it converge to the SAME shape.
TWO design points the user corrected me on, BOTH load-bearing:
  (1) STORE THE PATH, don't erase — `⟨CARRIER⟩` is a PACKED node (SPPF): it converges for clustering
      (the key is `⟨CARRIER⟩`) AND `unhold_path[nid] = the original carrier` records HOW it converged,
      so the abstraction is `⟨CARRIER⟩ = recon q b r` (converged quotient + recoverable residue), never
      a lossy rewrite. (I first wrote a childless atom that discarded the carrier — never-discard-residue.)
  (2) The GRANULARITY of Agda records (structure fragmented across uniquely-named projection units, the
      record unit tiny) is NOT a wall — it is WHAT `--recursive` IS FOR. `jea_pysim --recursive` reads
      INTERIOR-node fan-in (shared structure inside the residue), not per-unit support overlap. Measured:
      `--recursive` alone → the recursive-shared section is EMPTY; `--recursive --unhold` → `⟨CARRIER⟩`
      is the top shared interior template across 68 units (UPArrow²'s and GradedRigCat's fields both
      project it). The shared carrier-template that per-unit `--clusters` could not aggregate is exactly
      the interior fan-in `--recursive` surfaces. **I declared a premature WALL (necessary-not-sufficient,
      "two walls") — the wall-before-declaring/rebuild-reflex misfiring; the user's two pointers dissolved
      it.** The RIGHT invocation is `--recursive --unhold` (interior template) and/or `--shape --unhold`
      (cross-carrier shell); NOT `--clusters --unhold` alone (blind to the fragmented shape).
Residue that legitimately remains: UPArrow²↔rig-cat is also a REDUCT (UPArrow² = 3 carrier-fields =
the L2 slice; the rig cat = 2 carriers + braids + laws), so they SHARE the ⟨CARRIER⟩ template but are
not identical — the detector surfaces the shared template (a real, ranked candidate), and the reduct
judgment ("UPArrow² is the L2 slice of the rig tower") is the semantic last step. Sibling of
[[similarity-not-grep]] — next rung: structural → structural-modulo-un-hold, via `--recursive`.
PROPOSAL-general-reconstruct-frontend (rev.2) supplies the un-hold primitive emit-only; `--unhold`
wires it into dedup as a packed-node normalization, path-preserving.
Related: [[set1-is-grade-collapse]], [[duality-operator-either-trap]], [[adjunction-is-the-wedge-residue-counit]].
