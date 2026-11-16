---
name: cong-trans-extraction
description: "Foundation.Eq trio cong-trans / sym-trans / trans-sym extracted as iterated-SPPF cluster-seeds; arc closed across 67 files / 346 sites; kernel↔predicate bridge pattern surfaced as next-arc candidate."
metadata: 
  node_type: memory
  type: project
  originSessionId: d49d2868-8ade-4add-9d72-b31958685ef0
---

`Substrate.Foundation.Eq.cong-trans f p q = trans (cong f p) q` is the naturality-square step packaged as one inference rule. Recognises the most frequent cross-cutting Eq sub-shape across the repo (338 `trans (cong …` occurrences in 124 files at extraction time).

**Why:** demonstrates the iterated-SPPF claim — extracting small composable primitives makes their adoption-sites form new syntactic clusters on next similarity-script pass. Pre-extraction, sites used `trans (cong f X) Y` as 3 tokens in a chain-cong pattern only detectable at sub-expression scale; post-extraction, sites use `cong-trans` as one substrate-named token, so token-bag similarity rises and skeleton overlap becomes mechanically visible.

**How to apply:** when typed-holes / SPPF inspection of an enumeration-of-content cluster surfaces a recurring sub-expression shape (not text) appearing across taxonomically distinct branches, extract it as a named combinator in the deepest applicable Foundation/categorical module. Re-run similarity script; new clusters form around the named primitive's adoption sites. See [[cluster-action-methodology]] for the parent workflow.

**Initial migration cohort:** 6 files in `Substrate/Algebra/F2/HodgeDim4/ReservedBridgeAlternatives/{Swap,Cyclic}/Lookup{0,1,2}.agda`. Skeleton dump after migration shows Cyclic/Lookup0 ↔ Swap/Lookup1 are 18/20 lines literally identical (only file-header / bridge-name tokens differ). The chain-cong proof body collapses to a single substrate-named pattern.

**Scorer caveat:** the agda_similarity geomean across char3/token/line/block collapses to 0 when block-scale similarity is 0 (union-find smearing protection). The cohesion *exists* at token-scale (1.000) but is masked. To see post-extraction clusters, use `--skeleton --typed-holes` mode (which works at the parametric-skeleton level rather than geomean cohesion) until / unless the script gains a per-scale clustering option.

**Sibling sites still using raw shape:** ~324 remaining occurrences in 122 files. Migration is opportunistic — when touching a file with `trans (cong …)` in the proof body, swap to `cong-trans` to grow the cluster footprint.

## Round 2: sym-composition dual pair

Added two more Eq combinators packaging the dual `sym` shapes (72 + 81 occurrences across the repo at extraction):

- `sym-trans : x ≡ y → x ≡ z → y ≡ z` (`trans (sym p) q` — shared **source** triangle)
- `trans-sym : x ≡ y → z ≡ y → x ≡ z` (`trans p (sym q)` — shared **target** triangle)

Migrated 20-slice cohort (round 2):

- `Substrate/Groups/S4-Iso/ExtractCorrect.agda` — 16 sites of `trans X (sym Y)` across the `apply-inj` case analysis collapsed to `trans-sym`; `apply-inj` itself uses `sym-trans` + `cong-trans`.
- `Substrate/Groups/Stab-S3.agda` — `σ-injective`, `stab-preserves-≢`, `Stab-inv` (Stab-S3 + Subgroup share an identical `sym-trans (cong …) (inv-l …)` body for the inv-action stabilizer proof).
- `Substrate/Groups/Subgroup.agda` — `Stab-resp-≈`, `V₄-image-Subgroup` carrier proof, etc.
- `Substrate/Groups/S4-Iso/Embedding.agda` — `s3-apply-inv-r` and `s3-inv-apply-l` (the round-trip chain on both sides).
- `Substrate/Groups/S4-Iso/ForwardHom.agda` — top-level `forward-hom = trans-sym LHS RHS`.
- `Substrate/Groups/Coxeter/Core/NormalizeAppend/{Left,Right}.agda` — chirality pair migrated together (13/20 lines now identical post-migration).
- `Substrate/Groups/Coxeter/Core/NormalizeCong/{Left,Right}.agda` — chirality pair using sandwich `trans X (trans-sym Y Z)`.
- `Substrate/Groups/V4/FourProduct.agda` — `≢→≉` (sym-trans normalize-anchor chain), `bridge` (full cong-trans / sym-trans sequence).
- `Substrate/Groups/V4/Axioms/Lifted.agda` — `·-assoc-Word`, `·-right-cancel-ε`.
- `Substrate/Groups/V4-Coxeter.agda` — `flatten-product`, `insert-append-lemma-V4` case AB.
- `Substrate/Groups/V4-Embedding.agda` — `act-axis-id`, `act-axis-∙`, `act-axis-involutive`.

## Discovery via typed-holes

Round 2's later migrations were discovered by running `agda_similarity --skeleton --typed-holes` on high-similarity pairs surfaced by `--top 20`. The chirality pairs (NormalizeAppend/{Left,Right}, NormalizeCong/{Left,Right}) showed 13–15 / 19–20 lines identical with 2 residue tokens each — a clear signal of mirror-pair structure that the substrate's chirality-pair-completeness discipline already enforces at the file boundary.

The script's hole-identification didn't find a *new* primitive in round 2 — every high-similarity pair turned out to share the trio's three shapes. That itself is a result: at the current extraction level, `cong-trans / sym-trans / trans-sym` saturates the high-frequency naturality-square / triangle structure in the substrate. Further extractions would need to target *categorically* deeper patterns (e.g., 2-cell coherence, naturality squares involving two cong'd legs).

## Verification scope

Round 2 verification was per-file + by aggregate roots (`Substrate/Groups/S4-Iso.agda`, `Substrate/Groups/Coxeter/Core.agda`, `Substrate/Groups/V4.agda`) rather than via `Substrate.All.agda`. The latter OOMed (SIGKILL, exit 137) on this machine even before the changes — a known scaling limit of the dependency-graph closure. Aggregate-root typechecks cover the full dependency closure of the migrated files transitively.

## Arc closure (rounds 3-7)

After round 2 the arc continued through five more migration cohorts before reaching closure:

- Round 3 — multi-production cohort (`136c901`, 7 files, both cong-trans + sym-trans).
- Round 4 — sym-trans arc closure (`4b49216` F2CubedPuncturing, single file).
- Round 5 — HodgeDim3/MetricGauge cohort (`b2050d4`, 5 files).
- Round 6 — SymBilinForm cohort (`c0c6983`, 2 files) + ReservedBridge (`63200fe`, 1 file).
- Round 7 — Algebra/F2 + Geometry/HodgeDim3 cohorts (`bddf677`, 5 files) + final scattered closure (`b0fdf7b`, 6 files).

**Final adoption (commit `c6ae7f6`, all arcs closed):**

| Production   | Files | Total sites |
|--------------|-------|-------------|
| `cong-trans` |    40 |         222 |
| `sym-trans`  |    17 |          52 |
| `trans-sym`  |    10 |          72 |
| **Total**    |    67 |         346 |

**Rejected false positives (3, all documented as C5.1.2.2 catalogue seeds):**

- `Foundation/Eq.agda` — self-reference (cong-trans definition itself).
- `Foundation/Hedberg.agda` — local `trans-sym-id` lemma.
- `Algebra/F2/HodgeDim3/MetricGauge/CongruenceBridge.agda` — `congruence-*` identifier-prefix matches the grep regex.

## Saturation confirmed; kernel↔predicate bridge surfaced as next-arc candidate

Post-arc similarity-script run on all 40 cong-trans adopters: top similarity pair S1S2CubedOnE1 ↔ S1S2CubedOnE2 at 0.61 (geomean) / 1.000 (token-bag). Many cross-file pairs at 0.93-1.000 token similarity — confirms the cluster-seeding effect.

`--skeleton --typed-holes` on ChiralityAxis ↔ V4Plane (cross-family Geometry/HodgeDim3 pair) surfaced a new structural pattern: the **kernel↔predicate bridge**. Both files share 18 lines of skeleton for their `pred→kernel` and `kernel→pred` proofs. After trio adoption the bodies read:

```agda
pred-i = sym-trans (<selector-lookup-i> w)
                   (cong-trans (λ x → lookup x i) ker (lookup-𝟎 i))
```

This is a substrate-level discipline pattern (not an Eq primitive). The bridge appears wherever a linear-subspace is encoded as both a Pred and a Kernel: V4Plane (1-dim), ChiralityAxis (2-dim).

## KernelPredBridge extraction (commit `30eb9b7`)

Extracted as `Substrate.Algebra.F2.Linear.KernelPredBridge` with two micro-lemmas, each a one-line composition of the trio with `lookup-𝟎`:

```agda
pred-at-i→kernel-at-i _ _ i sl pi  =  trans-sym (trans sl pi) (lookup-𝟎 i)
kernel-at-i→pred-at-i _ _ i sl ker =  sym-trans sl (cong-trans (λ x → lookup x i) ker (lookup-𝟎 i))
```

Migration: ChiralityAxis + V4Plane both routed through the bridge. Per-site body went from ~3 lines per index to one bridge-call per index. The 2 confirmed call sites are the only direct bridge-shape sites in the substrate (verified by survey).

## Saturation at this depth

Post-bridge survey confirmed saturation of "post-trio" extractions at this level:

- **Hamming codes** (`H-7-4-3`, `H-8-4-4`) use single-matrix parity-check, not per-component predicate decomposition. They define `KernelCode` but don't expose `pred→kernel`/`kernel→pred` API. Not bridge sites.
- **Cocycles/M-11 files** have no `pred→kernel`/`kernel→pred` usage. Not bridge sites.
- **Broader typed-holes** on all 48 production-using files: top non-trivial pair (S1S2CubedOnE0 ↔ E1 in the MetricGauge cohort) shares 9/18 lines but **template-only, not body** — different orbit-specific lemma applications at the same 5 nested cong-trans positions. Extracting a parametric "cubed-on-orbit" lemma would be over-decomposition (~25 lines of parametric machinery vs 30 saved across 3 sites).

The trio + bridge pair has saturated the substrate's "iterated-SPPF" extraction surface at depth-2. Further extractions would need: (a) a deeper architectural pattern that the trio surfaces at depth-3, (b) a NEW family the trio doesn't touch, or (c) cross-domain bridges between currently-distinct substrate cocycle clusters.

**Γ-store post-arc (5 productions, 67 file-adoptions, 352 sites):**

| Production              | Files | Sites |
|-------------------------|-------|-------|
| `cong-trans`            |    40 |   222 |
| `sym-trans`             |    17 |    52 |
| `trans-sym`             |    10 |    72 |
| `pred-at-i→kernel-at-i` |     2 |     3 |
| `kernel-at-i→pred-at-i` |     2 |     3 |
