---
name: hh-arc-prime-sampled-chain
description: "HH-arc three-crumb prime-sampled chain context: each emission's context is 3 V₄-coset crumbs from past chain symbols at offsets (1, p, q) for primes p, q. HH4 MI sweep: past-chain-v4 (p=2, q=3) wins on all corpora 13.5%-82.2% of H(chain). HH7 simulated per-emission cost reduction 1.6%-66% vs unigram. HH8 Hamming recovery rate 6.7%-21.2% on mispredicts"
metadata: 
  node_type: memory
  type: project
  originSessionId: bb094a39-05c5-494d-8b01-cc34809ccae9
---

HH-arc closure summary. Triggered by the user 2026-05-21:
'connect the three axes to three crumb samples spaced apart ...
those crumb samples' period tested at different prime intervals ...
how to construct richer chain physics here.' Plus the user's
correction on GG-arc over-claiming.

**Architectural choice (per user Q3):** parallel feature stream
(predictor context), not chain-walk replacement. Lower architectural
risk; chain reversibility preserved.

**Axis assignment survey (per user Q1):** four variants tested in
HH4. Past-chain-v4 won; bit-stream variants were ENCODER-ONLY (not
decoder-symmetric due to forward-bit dependence at decode time).

**Costructure (DBE shadow):** `PrimeContext(p, q) =
(v4_part(chain[k-1]), v4_part(chain[k-p]), v4_part(chain[k-q]))`
∈ {0..3}³ = 64 values. Per emission, context is computed from
chain_terminals history; both encoder and decoder can compute it.

**Entailment chain:**
  (HH-E1) Predictive capacity: MI(prime_context; chain_symbol) > 0
          on all tested corpora. **CONFIRMED.**
  (HH-E2) Per-emission cost under prime-context predictor < unigram
          baseline. **CONFIRMED in simulation** (1.6%-66% reduction).
  (HH-E3) Hamming(7,4) syndrome recovery captures mispredict cases.
          **PARTIALLY CONFIRMED** (6.7%-21.2% recovery rate).
  Codec wiring: DEFERRED to follow-up arc.

**Slices landed (all 10):**

  HH1 — `eliza/prime_chain.py`. `sample_three_crumbs(bits, k, p, q)`
        returns (c0, c1, c2). `prime_chain_stream` builds streams
        with parameterised step stride and axis assignment.
  HH2 — Axis assignment survey: 4 variants ({v4-abelian,
        v4-s3-chirality, s4-quotient, s3-abelian}). HH4 found
        v4-abelian dominates (same as v4-s3-chirality up to
        relabelling); s4-quotient/s3-abelian lose information.
  HH3 — `mutual_information(target, context, n_target_vals)` returns
        (H(target), H(target|context), MI). Identity check + random
        check pass.
  HH4 — Two MI sweeps:
        First pass: `test_hh_arc_prime_sweep.py` uses bit-stream
        sampling at (k, k+p, k+q). High MI (53.1% on t1t2 at (7, 13)).
        ⚠ I INITIALLY DISMISSED this as "encoder-only because the
        decoder lacks future bits". Per user correction 2026-05-21:
        'that depends on if you think of the decoder as living at
        the start or end of its rewrite window'. Under WINDOWED
        decode (decoder produces a batch of bits before the next
        context evaluation), forward bits within the just-decoded
        window ARE available. Bit-stream context at offsets up to
        the window's reach IS decoder-symmetric. The 53.1% MI on
        t1t2 at (p=7, q=13) and 19.2% on substrate_opcodes at
        (p=5, q=7) are usable under a windowed-decoder architecture.
        Second pass: `test_hh_arc_past_chain_mi.py` uses PAST
        chain-symbol V₄-parts. Symmetric under streaming decode
        too. **Best (p, q) = (2, 3) on every corpus** under this
        more-conservative streaming model:
          substrate_agda:    MI = 0.622 bits (13.6% of H(chain))
          substrate_memory:  MI = 0.618 bits (13.5%)
          substrate_opcodes: MI = 1.441 bits (70.5%)
          t1t2_handcrafted:  MI = 2.631 bits (82.2%)
  HH5 — `eliza/prime_context_predictor.py: PrimeContextPredictor`.
        64-bucket adaptive predictor; `set_context(value)` is called
        per emission with the past-chain V₄ context value.
        `_V4_PART_TABLE` cached from `coarse_residue.coset_members`
        (FF-arc).
  HH6 — V7 wiring DEFERRED in favour of simulation-based measurement
        (HH7). Full V7 wiring requires restructuring _build_predictors
        + threading context through emission paths, which is more
        invasive than this arc's scope.
  HH7 — `test_hh_arc_compression_simulation.py`. Simulated per-
        emission cost under Laplace-smoothed adaptive predictors:
        unigram baseline vs 64-bucket prime-context (p=2, q=3).
          | corpus           | bpb_uni | bpb_prime | Δ      |
          |------------------|---------|-----------|--------|
          | substrate_agda   |  4.600  |   4.521   | -1.7%  |
          | substrate_memory |  4.606  |   4.534   | -1.6%  |
          | substrate_opcodes|  2.072  |   0.820   | -60.4% |
          | t1t2_handcrafted |  3.227  |   1.088   | -66.3% |
        **IMPORTANT CAVEAT (per [[negative-findings-corpus-bound]]):**
        This is SIMULATED per-emission cost vs UNIGRAM. Not actual
        codec compression. The real codec already has Bigram /
        ChamberContext / QuaternionContext predictors that capture
        SOME of this signal; gain over the CODEC's best predictor
        (not unigram) would be smaller. Real codec wiring needed
        for honest compression measurement.
  HH8 — Hamming(7, 4) recovery rate on mispredict cases. When
        prime-predictor's top guess ≠ actual emit AND P(emit|ctx) <
        1/3, check Hamming-distance-1 recovery via the chamber-
        index XOR weight:
          substrate_agda:    19.5% of mispredicts within Ham-dist 1
          substrate_memory:  21.2%
          substrate_opcodes:  6.7%
          t1t2_handcrafted:  18.2%
        The structured corpora (opcodes, t1t2) have LOWER recovery
        rate because their mispredicts cluster at structurally-
        distant chambers; natural corpora (agda, memory) have
        HIGHER recovery rate because mispredicts are nearer.
  HH9 — `Substrate.Category.PrimeSampledChain` Agda primitive under
        `--safe --without-K`. Records: `PrimePair`, `Crumb`,
        `ThreeCrumbContext`, `V4PartExtraction`,
        `PrimeContextPredictor`, `SymmetricContextProperty`,
        `HammingMispredictRecovery`.
  HH10 — this capstone.

**Decoder-window correction (per user 2026-05-21):**

The first-pass MI sweep with bit-stream context was prematurely
dismissed as encoder-only. The actual usability depends on the
decoder's window architecture:

  Streaming decode (decoder head moves one symbol forward at a
    time): only PAST bits / past chain symbols available; long-range
    bit-stream context isn't usable.

  Windowed decode (decoder produces a batch of bits per window
    boundary): forward bits within the just-completed window ARE
    available before the next context evaluation. Bit-stream context
    at offsets up to the window's reach IS usable.

Under the windowed model, the high-MI bit-stream results from the
first-pass sweep RE-OPEN as candidate predictor contexts:
  substrate_opcodes (p=5, q=7, v4-abelian): 19.2% MI
  t1t2 (p=7, q=13, v4-abelian):              53.1% MI
The substrate codec already operates in windows for some passes
(rule-body emission, backref expansion), so the windowed model is
realistic to engineer. The streaming-only assumption was MINE,
not the codec's.

**The structural finding (without over-claiming):**

The past-chain-symbol V₄-coset context has measurable mutual
information with the next chain symbol. The strongest signal under
the streaming-decode model is at short prime distances (p=2, q=3)
— close-range correlations dominate. Long-range primes also have
decent signal (10-77% MI for p ∈ {7, 11, 13}) but never beat (2, 3)
under streaming.

Under the WINDOWED-decode model, long-range bit-stream context
becomes available; the first-pass sweep's (p=7, q=13) at 53.1% MI
on t1t2 represents a meaningfully richer gauge axis than past-
chain-symbol-only context can reach.

In simulation against unigram, the prime-context predictor would
substantially reduce per-emission cost on highly-structured corpora
(60-66%) and modestly reduce it on natural-language-like corpora
(1.6%). This says nothing definitive about actual codec compression
gain — the codec's existing predictors (BigramPredictor +
ChamberContextPredictor + QuaternionContextPredictor) already
capture some of this signal.

**The interesting structural fact:** the (p=2, q=3) winner across
all corpora suggests that the substrate codec's chain walk has
genuine 2-step and 3-step Markov correlations that aren't fully
captured by the 1-step ChamberContextPredictor (which uses ONLY
chamber at k-1, not (k-1, k-2, k-3) jointly). The HH-arc identifies
a clean potential extension: a Trigram-style ChamberContextPredictor
keyed on past V₄-parts at (k-1, k-2, k-3).

**Per the user's "richer chain physics" framing:**

The "richness" turned out NOT to be from prime intervals far apart
(which the bit-stream MI sweep suggested but couldn't be wired
decoder-symmetrically). It came from the JOINT 3-crumb V₄ context
at NEAR-PRIME distances (1, 2, 3). The substrate's chain physics
has short-range non-Markov structure that single-step Markov
predictors miss.

**Per [[chain-walk-blocks-rotation-factor]]:** the cumulative chain
state past k carries information about future emissions that the
single-step transition cannot factor. HH4's MI measurement
quantifies this directly.

**Per [[expose-generator-not-orbit]]:** (p, q) is the gauge
generator; per-corpus best (p, q) is an orbit. The atlas of
(p, q) → MI is the generator-orbit reading.

**Per [[3plus1-parity-universal]]:** 3 crumbs at distances (1, p, q)
realise 3 axes; the choice of (p, q) ordering vs (q, p) is the
chirality F₂.

**Per [[multi-reading-ambient-discipline]]:** the (p, q) sweep
matrix IS the substrate-honest reading; reporting only the best
(p, q) hides the gauge.

**Per [[negative-findings-corpus-bound]]:** the 60-66% per-emission
reduction is bounded to {simulated vs unigram, 4 corpora, 2KB
size, prime set {2, 3, 5, 7, 11, 13}}. Real codec compression
gain expected to be SMALLER.

**Follow-up arcs (II-arc candidates):**
  1. Actual V7 wiring of PrimeContextPredictor; honest bpb gain vs
     V7's actual best predictor (Bigram / ChamberContext / Quaternion).
  2. Per-corpus (p, q) auto-discovery + header byte to ship the
     chosen pair (similar to bit_shift header).
  3. Hamming-syndrome recovery wired into the codec's decoder at
     mispredict positions; quantify codec-as-ECC capacity uplift.
  4. Triple-V₄ predictor variant: extract V₄ parts at (k-1, k-2,
     k-3) without prime parameter (effectively (p=2, q=3) hardcoded).
     Compare to general (p, q) sweep.
  5. Crumb derivation alternatives: instead of v4-coset-position,
     use S₃-quotient or chirality-projection from chain symbols.
     Survey predictive capacity.

Related: [[gg-arc-multiprime-spectral]] (sibling arc — both probe
prime-structured input properties, but GG analyses input bits and
HH samples chain history);
[[ff-arc-coarse-residue]] (FF's NIBBLE_TO_PERM image bijection is
the "current chain step" version of HH's "past chain symbols"
context);
[[ee-arc-reed-muller-hierarchy]] (HH8's Hamming(7,4) recovery
reuses EE6's runtime);
[[dd-arc-clifford-graded-emission]] (HH's V₄-coset position is
the Λ²-grade reading at the chain symbol layer);
[[chain-walk-blocks-rotation-factor]] (the structural fact whose
MI face HH4 measures);
[[expose-generator-not-orbit]] ((p, q) gauge generator);
[[3plus1-parity-universal]] (3 crumbs + chirality F₂);
[[multi-reading-ambient-discipline]] ((p, q) sweep matrix);
[[negative-findings-corpus-bound]] (simulated cost reduction
bounded vs unigram + tested corpora).
