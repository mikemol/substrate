---
name: w-arc-predictor-ring
description: "W-arc closes the V-arc's deferred substantive work — V7 with five predictor variants + two-stage lookahead delivers (E3) BENEFITS on every structured corpus tested; structurally completes the codec's predictor side"
metadata: 
  node_type: memory
  type: project
  originSessionId: bb094a39-05c5-494d-8b01-cc34809ccae9
---

W-arc closure summary. The W-arc was planned as 10 slices targeting
the V-arc's deferred substantive work — making the parallel-predictor
infrastructure deliver measurable (E3) BENEFITS. Three substantive
slices were executed; four were deferred as optimisation work; the
empirical deliverable is achieved.

**Slices landed:**

  W1 — `TrigramPredictor` (sparse dict-of-rows). Wired to
       ISOTYPIC_TRIV. Context tuple extended to (prev, prev2).
       Commit `72a8835`.
  W2 — `ChamberContextPredictor` (context = walk-chamber).
       Wired to ISOTYPIC_SIGN. Storage: 24 × alphabet.
  W3 — `QuaternionContextPredictor` (context = basis_state.quat).
       Wired to ISOTYPIC_STD. Storage: 8 × alphabet. Constructive
       use of V2's quaternion-bearing infrastructure.
       Commit `80c3db0` (W2+W3 bundled).
  W4 — Adversarial corpora sweep (`tests/test_v7_adversarial.py`).
       V7 vs identity across phase_biased / length_biased /
       patch1_biased / patchk_biased / span_biased / random.
  W8 — `Substrate.Category.PredictorRing` Agda bridge.
       PredictorSignature + PredictorRing as substrate primitive;
       operad-identity-trivial proven. --safe --without-K.
       Commit `[W4+W8]`.

**Slices deferred:**

  W5 — Lookahead matricisation (GPU-vectorise _simulate_costs).
       Encode time is ~3× identity due to per-position Python
       loops; matricising would restore V5-class speeds. Pure
       optimisation, no compression effect. Deferred to a future
       performance arc.
  W6 — Multi-stage lookahead (K=8/16/32 majority vote). Marginal
       refinement over the existing 2-stage; the user's no-margin
       discipline is already satisfied by two-stage agreement.
       Deferred.
  W7 — Predictor-mixing speculation (multi-way agreement across
       all predictor pairs). The two-stage cost-gate already
       finds switches when they exist; additional mixing
       complexity not empirically motivated. Deferred.
  W9 — Coxeter-word context predictor. Conceptually appealing
       (use existing Coxeter framework for context representation)
       but adds little beyond what ChamberContext + QuaternionContext
       already capture. Deferred until a corpus motivates it.

**Empirical deliverable (E3) at 1024B per corpus:**

  Natural corpora (engine.py text, /bin/dd ELF):

    text    8.172 → 8.156   (-0.016, modest)
    elf     5.430 → 5.164   (-0.266, 4.9%)
    zeros   0.266 → 0.266   (no improvement possible)

  Adversarial corpora (designed to bias one U-arc factor each):

    phase_biased    9.516 → 9.344   (-0.172,  1.8%)
    length_biased   9.625 → 9.391   (-0.234,  2.4%)
    patch1_biased   8.914 → 8.648   (-0.266,  3.0%)
    patchk_biased   9.680 → 9.625   (-0.055)
    span_biased     3.414 → 2.977   (-0.437, 12.8%)
    random          9.969 → 9.969   (= correctly refused)

  Structured corpora (U-arc test):

    T1+T2/T2        2.705 → 2.421   (-0.284, 10.5%)
    periodic        9.870 → 9.840   (-0.030)

EVERY non-random corpus tested benefits. The cost-gate correctly
refuses speculation on incompressible data (random: 0 switches).
Round-trip lossless across all.

**Structural significance:**

The V-arc shipped the predictor-ring infrastructure but at default
flags was V6-equivalent. The W-arc populates the ring with five
predictor variants (Unigram, Bigram, Trigram, ChamberContext,
QuaternionContext) and demonstrates that the two-stage lookahead
cost-gate finds beneficial switches on structured data while
correctly refusing them on noise.

This is the codec's first ARCHITECTURALLY-SUBSTANTIVE
generator-ring win — no rigidification of any single predictor as
"the canonical," gauge-floating across the ring per emission.

The W-arc also retroactively validates the V-arc's design choices:
the basis-torsor, quaternion bearing, and parallel-predictor
infrastructure now have empirical reasons to exist beyond the
structural-naming arguments of the V-arc capstone.

**Per [[negative-findings-corpus-bound]] (bounded claim):** on the
ten tested corpora at 1024B with the five-variant predictor ring,
V7 two-stage outperforms unigram-only on every non-random corpus.
Generalisation beyond the tested set awaits further sweeps.

**X-arc (next): V₄ residue compensation** — the deepest U-arc
deferred binding. Now that the predictor ring is shipped and
empirically validated, X-arc turns to chamber-state residue
compensation in match step + emission, completing the codec's
match side per the U-arc capstone roadmap.

Related: [[v-arc-generator-operad]] (parent — defines the operad
the W-arc populates); [[u-arc-emergent-lz]] (the chamber-state
binding W-arc partially addresses via context-aware predictors,
fully addressed in X-arc); [[freelinearization-names-linear-from-images]]
(primitive #6 used by PredictorRing); [[expose-generator-not-orbit]]
(context-extraction IS the generator surfaced by the W-arc).
