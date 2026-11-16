---
name: x-arc-residue-compensation
description: "X-arc began with the ResidueCompensation Agda primitive naming the chamber-state binding compensation; runtime implementation (X3-X7) deferred — the W-arc's ChamberContextPredictor addresses the same binding from the probability side"
metadata: 
  node_type: memory
  type: project
  originSessionId: bb094a39-05c5-494d-8b01-cc34809ccae9
---

X-arc partial closure. The X-arc was planned as 10 slices targeting
the U-arc's deepest deferred binding (chamber-state residue
compensation in the match step) plus the V-arc's deferred range-coder
bit-granular sink work. One substantive structural slice (X8 Agda
bridge) landed; the runtime work (X1-X7) is documented and deferred.

**Slices landed:**

  X8 — `Substrate.Category.ResidueCompensation` Agda bridge.
       Names the V₄ residue compensation as a categorical primitive
       parameterised over the chain-symbol carrier. Includes
       `FullResidueCompensation` for S₄ extension. Trivial
       soundness inhabited under refl placeholder; full soundness
       requires the chamber-walk semantics at the categorical layer
       (deferred). Under --safe --without-K.

**Slices deferred:**

  X1+X2 — Range-coder rewiring for true `S_SHIFT_BIT` bit-granular
       sink + codec stacking. The codec's range coder already
       drives bit-granular output internally; making the opcode
       actually gate bit release requires substantial coder
       reengineering. Deferred until codec composition use case
       arises.
  X3+X4 — V₄ residue match-step + emission. Track per-rule
       growth-context (chamber state at growth time); extend
       match-tensor to consider σ-rotated bodies; encoder emits
       via `RuleAction.residue`; decoder applies σ to body. The
       Agda bridge X8 names the structure; runtime work pending.
  X5 — V₄ residue alias re-sweep. Re-runs adversarial corpora with
       V₄ residue compensation active; verifies the U-arc's
       alias-define mechanism (commit `a016442`) now BENEFITS on
       previously-regressing corpora.
  X6 — Full S₄ residue extension (24-permutation orbit).
  X7 — Basis-aware emission alphabet (different emit alphabet per
       BasisLabel, not just per-predictor).

**Why the deferral is honest:**

The W-arc's `ChamberContextPredictor` already addresses the
chamber-state binding from the PROBABILITY-CONDITIONING side. On
the adversarial corpora sweep (commit `[W4+W8]`):

  phase_biased    9.516 → 9.344   (-0.172,  1.8%)
  length_biased   9.625 → 9.391   (-0.234,  2.4%)
  patch1_biased   8.914 → 8.648   (-0.266,  3.0%)
  span_biased     3.414 → 2.977   (-0.437, 12.8%)

These are corpora the U-arc's alias-define mechanism FAILED on
(regressed). The W-arc's ChamberContextPredictor SUCCEEDS on them
because it captures P(emit | chamber) directly. The geometric V₄
residue match-step is a complementary mechanism; on these corpora
it would likely ADD modest gains but doesn't bear the empirical
load that the predictor side does.

For future X3-X7 execution, the priority would be:
  1. X3+X4 on corpora where ChamberContextPredictor's gains
     plateau (likely longer streams or non-text data).
  2. X1+X2 when codec composition becomes a use case.
  3. X6 (full S₄) only if V₄ alone is empirically insufficient.

**Substrate alignment:**

Per [[homology-cohomology-recursion]]: the predictor approach
(probability conditioning) is COHOMOLOGY-side compensation —
catalog the frequencies. The residue approach (geometric σ-rotation)
is HOMOLOGY-side compensation — apply the group action to the
observed pattern. Both are valid readings; the W-arc closed the
cohomology side, the X-arc names the homology side at the
categorical layer.

The Agda bridge X8 (`Substrate.Category.ResidueCompensation`)
stands as the substrate-side definition; the Python runtime
implementation joins when the empirical case justifies it.

**Y-arc target candidates** (next):

  1. **Encoder time matricisation** (W5 deferred). The V7 encoder
     is ~3× slower than V6 due to per-position lookahead
     simulations. GPU-vectorise `_simulate_costs` (per
     [[matrix-op-homoiconicity]]) to restore V5-class speeds
     while keeping the W-arc compression wins.
  2. **Predictor mixing** (W6/W7 deferred). Mixture-of-experts
     speculation across the full predictor ring.
  3. **X3+X4 V₄ residue runtime** if a corpus emerges where the
     predictor-side W-arc work plateaus.
  4. **Substrate self-application** — V7 on substrate-internal
     data (Agda source, MEMORY.md). The substrate's structural
     properties should compress well under V7's chamber-context
     predictors.

Related: [[w-arc-predictor-ring]] (parent — the predictor side
that empirically addresses the same binding); [[u-arc-emergent-lz]]
(the chamber-state binding diagnosis); [[v-arc-generator-operad]]
(the operad framework X8's primitive instantiates).
