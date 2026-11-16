---
name: ff-arc-coarse-residue
description: "FF-arc emits AA-arc S₄ residue σ via S_COARSE_REF + 4-bit nibble alphabet when σ falls in NIBBLE_TO_PERM image (16 of 24 chambers); lossless round-trip lands; compression-wise neutral (-0.7% to +0.2% across corpora) because adaptive predictor handles distribution efficiently. Structural finding: 67-100% of empirical σ cluster in chain-walk image"
metadata: 
  node_type: memory
  type: project
  originSessionId: bb094a39-05c5-494d-8b01-cc34809ccae9
---

FF-arc closure summary. Triggered by the user's "sloppy + recover
via EE7" prompt: 'with EE7, we could permit ourselves to get a
little sloppy and use EE7 to recover without preserving as much
residue.'

**Costructure (DBE shadow):** the σ ∈ S₄ residue's domain
decomposes into:
  image     = NIBBLE_TO_PERM image (16 chambers reachable as
              single-step chain-walk transitions)
  off-image = S₄ \\ image (8 chambers requiring multi-step structure)

Encoder emits σ_image via a 4-bit nibble alphabet (S_COARSE_REF);
σ_off-image falls back to the full 5-bit chamber alphabet
(S_REF_RECENT).

**Entailment chain:**
  (FF-E1) Bijection between NIBBLE_TO_PERM indices and chain-walk-
          image chambers is canonical (NIBBLE_TO_PERM is injective).
  (FF-E2) Round-trip lossless under S_COARSE_REF dispatch.
  (FF-E3) Empirical compression gain from smaller alphabet:
          conjectured ~0.58 bits/emission; **NEGATIVE FINDING** —
          adaptive predictor handles σ distribution efficiently
          regardless of alphabet size.

**Slices landed (all 10):**

  FF1 — `eliza/coarse_residue.py: _build_v4_coarse_map`. V₄ left-
        coset decomposition of S₄ → 6 cosets of size 4. **Structural
        finding: every (prev_state, V₄-coset) pair has EXACTLY 4
        candidate σ values.** V₄ coarsening alone is too coarse to
        disambiguate σ from prev_state. The 16 chain-walk transitions
        per prev_state distribute uniformly across the 6 cosets
        (16/6 ≈ 2.67 average, max 4 per coset). Recorded as negative
        baseline.
  FF2 — NIBBLE_TO_PERM image bijection. The 16 σ values reachable
        as single chain-walk steps form a proper subset of S₄.
        Image chamber indices = {0,1,2,3,5,9,10,11,12,13,14,18,20,
        21,22,23}; missing 8 = {4,6,7,8,15,16,17,19}.
        sigma_to_nibble / nibble_to_sigma bijection cached at
        module load.
  FF3 — V7 opcode `S_COARSE_REF` at slot 8. N_V7_CONTROL_OPCODES
        bumped 8 → 9.
  FF4 — Encoder dispatch: when `sigma_in_image(backref_sigma)` and
        `not disable_coarse_ref`, emit S_COARSE_REF with σ encoded
        as 4-bit nibble; else emit S_REF_RECENT with full chamber
        idx. Counter `n_coarse_ref` tracks how often coarse path is
        chosen.
  FF5 — Decoder unified dispatch: S_REF_RECENT and S_COARSE_REF
        share the 8-symbol payload reader; the coarse variant
        recovers σ via `nibble_to_sigma(sig_sym & 0xF)`.
  FF6 — Round-trip verified on substrate_opcodes / t1t2_handcrafted
        / substrate_agda at 2048 B with AA-arc speculate_backref +
        speculate_s4_residue active. All lossless under both
        coarse-on and coarse-off modes.
  FF7 — Empirical compression (2048 B, FF on vs FF off):
          substrate_opcodes:  142 → 141 B  (-0.70%) 100% coarse
          t1t2_handcrafted:   112 → 112 B  (0.00%)  100% coarse
          substrate_agda:    1620 → 1623 B (+0.19%)  67.2% coarse
        **Compression effect is essentially zero.** Reason: the
        adaptive predictor's range coder uses log₂(p) bits regardless
        of alphabet size; smaller alphabet doesn't save bits under
        an already-peaked predictor. The slight regression on
        substrate_agda (+3 bytes) is because the control opcode
        distribution splits across two slots (S_COARSE_REF and
        S_REF_RECENT), increasing the per-opcode cost.
  FF8 — Codec-as-ECC composition. With AA-arc backref active,
        single-bit-flip detection drops from EE8's 100% to ~83-90%
        on tested corpora. FF on vs FF off shows no material
        difference. AA-arc backref's compact encoding trades
        detection coverage for compression.
  FF9 — `Substrate.Category.CoarseResidueEmission` Agda primitive
        under `--safe --without-K`. Records: `CoarseResidueBijection`,
        `CoarseEmissionOpcode`, `EncoderDispatch`, `DecoderDispatch`,
        `LosslessCoarseRoundTrip`, `ChainWalkImageProperty`. States
        the empirical FF7 finding as commentary (not theorem).
  FF10 — this capstone.

**The substantive structural finding (FF7's negative-with-positive
reading):** 67-100% of the codec's empirical backref σ values fall
in the NIBBLE_TO_PERM image. This is an empirical confirmation that
the AA-arc backref-with-residue search ACTIVELY PREFERS single-step-
compatible σ values — backref expansions that flow smoothly into the
chain walk.

The "sloppy emission" framing succeeded as a bijection but not as a
compression win. The adaptive predictor already handles σ's
non-uniform distribution; emitting σ via a smaller alphabet is
redundant.

**Where the FF-arc concept WOULD compress (FF+1 arc):**
  1. Context-conditional predictor for σ: bind to prev_chamber +
     S_COARSE_REF vs S_REF_RECENT. Peaked per-context distributions
     would amplify the alphabet reduction.
  2. Lookahead-based recovery: emit σ_coarse + use next 3 chain
     symbols as syndrome to disambiguate σ_full. Requires decoder
     buffering.
  3. Hamming-syndrome bridge: map the 16 σ_image chambers to RM(1,3)
     codewords; emit only 4 message bits per σ + recover via syndrome
     from chain context.

**Per [[chain-walk-blocks-rotation-factor]]:** NIBBLE_TO_PERM image
= single-step chain transitions; σ ∈ image means the residue
"factors as one chain step", which the chain walk natively supports.
σ off-image means residue is multi-step, requiring composition
the chain walk can't factor.

**Per [[expose-generator-not-orbit]]:** the NIBBLE_TO_PERM image IS
the generator subset of S₄ relative to chain-walk transitions; FF-arc
surfaces this generator/orbit distinction at the opcode layer.

**Per [[3plus1-parity-universal]]:** |image| = 16 = 2⁴ = |V₄| × |S₃-inv|
— the substrate's V₄ × S₃-involution product naturally yields the
16-element subset.

**Per [[negative-findings-corpus-bound]]:** the compression-neutral
finding is bounded to tested corpora (substrate_agda, substrate_memory,
substrate_opcodes, t1t2_handcrafted) and tested settings (AA-arc
backref + S₄ residue active). Other configurations may differ.

**Per [[multi-reading-ambient-discipline]]:** the FF7 table reports
all corpora × FF on/off; no single reading is privileged.

**Per [[homology-cohomology-recursion]]:** chain-walk image
(layer-k) is the homology cycle; coarse-residue bijection (layer-k+2)
is the cohomology contraction; FF-arc closes the layer-k → layer-k+2
path.

**FF-arc structural deliverables:**
  • `S_COARSE_REF` opcode slot 8 (V7).
  • Lossless 4-bit-vs-5-bit σ alphabet split.
  • 67-100% empirical cluster in NIBBLE_TO_PERM image (named).
  • V₄-coarsening structural finding (FF1): too coarse to disambiguate
    σ from prev_state alone; recorded as negative result.

**Per the user's "EE7 recovery" framing:** the bijection IS the
recovery operator (lossless lookup). Hamming-style syndrome
recovery (where corruption is INTENTIONAL at the encoder) would
require chain-context lookahead at the decoder, deferred to FF+1.

Related: [[ee-arc-reed-muller-hierarchy]] (parent — EE7's Hamming
recovery prompted the FF-arc "sloppy + recover" framing);
[[dd-arc-clifford-graded-emission]] (Clifford grade hierarchy that
contains the S₄ residue as Λ²);
[[aa-arc-composed-reference]] (AA-arc's S_REF_RECENT σ that FF-arc
optimizes the emission of);
[[chain-walk-blocks-rotation-factor]] (the NIBBLE_TO_PERM image's
chain-walk significance);
[[expose-generator-not-orbit]] (generator/orbit distinction at the
σ alphabet layer);
[[3plus1-parity-universal]] (16-element subset as |V₄| × |S₃-inv|);
[[negative-findings-corpus-bound]] (bounded compression-neutral
result);
[[homology-cohomology-recursion]] (layer-k+2 closure).
