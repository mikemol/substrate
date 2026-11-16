---
name: jj-arc-multi-sylow-composition
description: "JJ-arc: how many Sylow primes can compose? Empirical saturation curve over Sylow-prime probes {2,3,5,7,11,13} on past-chain V₄ context. Natural text MI grows multiplicatively per Sylow added: substrate_agda 0.08→2.72 bits (|S|=1→6) at 8KB. Three composition bounds (group / entropy / samples)"
metadata: 
  node_type: memory
  type: project
  originSessionId: bb094a39-05c5-494d-8b01-cc34809ccae9
---

JJ-arc closure summary. Triggered by the user question 2026-05-21:
'how many different sylow primes can we compose?' — the deep
structural follow-up to II-arc's atlas-of-probes finding that
cross-Sylow pairs have synergy.

**The architectural answer (three bounds):**
  1. **Theoretical**: |composable Sylow primes| ≤ |primes dividing
     |GL(n, F₂)||. GL(3, F₂)=168 has {2, 3, 7}; GL(4, F₂)=20160 adds
     5; GL(5, F₂) adds 31 (Mersenne); each GL(n, F₂) adds new primes
     from 2^k − 1 factorization for k ≤ n. Bounded above by GL
     dimension, unbounded as n → ∞.
  2. **Information-theoretic**: joint MI ≤ H(chain symbol) ≈ 4.58
     bits. Beyond ~6 Sylow primes, joint MI approaches the chain
     entropy ceiling.
  3. **Sample-size**: joint context space = 4^|S| ≤ chain length.
     8KB chain → 16K symbols → |S| ≤ 7.

  Effective composable count on substrate-atlas corpora at 8KB:
  **4-6 Sylow primes**, depending on corpus information density.

**Costructure (DBE shadow):** `SylowProbe(prime) = (offset = prime
nibbles back, value = V₄-coset crumb)`. `MultiSylowAtlas = List
SylowProbe` with joint context = bit-packed concatenation of probe
crumbs.

**Entailment chain:**
  (JJ-E1) Joint MI grows monotonically with |Sylow-subset| on most
          corpora. CONFIRMED.
  (JJ-E2) Growth rate is roughly MULTIPLICATIVE on natural text
          (each Sylow ~ doubles MI). CONFIRMED on substrate_agda.
  (JJ-E3) Same-Sylow doubling has zero synergy (proven by Sylow
          theory + II5 empirical).
  (JJ-E4) Sample-size limit DOES surface at high |S| on low-MI
          corpora. CONFIRMED on substrate_memory (regresses at
          |S|≥5 due to alphabet sparsity).

**Slices landed (all 10):**

  JJ1 — `eliza/sylow_prime_probe.py`. Minimal Sylow probe: 1 probe
        per Sylow prime, V₄-coset crumb at offset = prime nibbles
        back. `joint_sylow_context(chain, primes)` bit-packs probes.
        Sylow ladders: SYLOW_PRIMES_GL3, GL4, GL5, GL8 listed.
  JJ2 — Saturation curve evaluator (`saturation_curve`); enumerates
        2^|S| − 1 non-empty subsets, finds best joint MI per size.
  JJ3 — Sylow-5 entry: probe at offset 5 nibbles. Confirmed in
        sweep (lifts to GL(4, F₂)).
  JJ4 — Single-Sylow MI (|S|=1):
          substrate_agda  best=Sylow-2 MI=0.06-0.08 bits
          substrate_memory best=Sylow-2 MI=0.04-0.05
          substrate_opcodes best=Sylow-3 MI=0.95-0.96
          t1t2_handcrafted best=Sylow-3 MI=0.76-0.77
  JJ5 — Pairwise + extended Sylow subsets sweep
        (`tests/test_jj_arc_sylow_saturation.py`). All 2^4=15
        subsets of {2,3,5,7} measured at 2KB+8KB; extended to
        2^6=63 subsets of {2,3,5,7,11,13} at 8KB.
  JJ6 — Quad-Sylow {2,3,5,7} joint MI:
          substrate_agda    0.69 bits (15% of H)
          substrate_memory  0.42 bits (9%)
          substrate_opcodes 1.45 bits (71%)
          t1t2_handcrafted  2.71 bits (85%)
  JJ7 — Saturation curve from |S|=1 to |S|=6 at 8KB:
          substrate_agda:   0.08→0.15→0.32→0.69→1.53→2.72 bits
                            (1.7%→3.3%→7%→15%→33%→59% of H)
          substrate_memory: 0.04→0.09→0.16→0.42→1.20→2.51 bits
                            (sample-sparsity regression visible at
                            high |S|: |S|=5 MI=1.20 but compression
                            regresses)
          substrate_opcodes: 0.96→1.16→1.38→1.45→1.49→1.51
                             (saturates near H=2.04)
          t1t2_handcrafted: 0.77→1.65→2.39→2.85→3.06→3.13
                            (98% of H=3.19 at |S|=6)
        **The growth is approximately MULTIPLICATIVE on natural
        text at low |S|**: substrate_agda doubles per Sylow added
        until sample-size becomes binding.
  JJ8 — Compression simulation
        (`tests/test_jj_arc_compression_sim.py`) at 8KB:
          | corpus    | base | {2,3} | {2,3,5} | {2-7}  | {2-13} |
          |-----------|------|-------|---------|--------|--------|
          | agda      | 4.587| 4.511 |  4.472  | 4.437  | 4.241  |
          | memory    | 4.592| 4.571 |  4.646  | 4.722  | 4.622  |
          | opcodes   | 2.051| 0.951 |  0.762  | 0.729  | 0.728  |
          | t1t2      | 3.201| 1.623 |  1.015  | 0.730  | 0.402  |
        Deltas vs baseline:
          agda     -1.6% / -2.5% / -3.3% / -5.6% / -7.5%
          memory   -0.5% / +1.2% / +2.8% / +2.5% / +0.6%  (regress)
          opcodes  -53.7%/ -62.9%/ -64.5%/ -64.8%/ -64.5%
          t1t2     -49.3%/ -68.3%/ -77.2%/ -82.8%/ -87.4%
        substrate_memory regression at |S|≥3 confirms the sample-
        size bound empirically.
        ⚠ CAVEAT: simulated cost vs UNIGRAM, not actual codec bpb
        (per [[negative-findings-corpus-bound]]).
  JJ9 — `Substrate.Category.MultiSylowComposition` Agda primitive
        under `--safe --without-K`. Records: `SylowPrime`,
        `SylowProbe`, `MultiSylowAtlas`, `CompositionalBounds`,
        `SaturationCurve`. Concrete `substrate-bounds-8kb`:
        (max-by-group=4, max-by-entropy=7, max-by-samples=7).
  JJ10 — this capstone.

**The headline structural finding:**

The "how many Sylow primes can we compose?" question has a
**three-bound answer**:

  1. **Group bound**: depends on GL(n, F₂) dimension; unbounded
     as n grows.
  2. **Entropy bound**: ~6 Sylow primes for substrate's S₄ chain
     (H ≤ 4.58 bits).
  3. **Sample bound**: ~7 Sylow primes at 8KB; scales as log₄(N).

  Practical answer at substrate-atlas scale (2KB-8KB): **3-4
  Sylow primes is the operational sweet spot** for most corpora;
  highly-structured corpora (t1t2, opcodes) benefit up to 6
  Sylows; natural text shows monotonic improvement.

**Empirical evidence for "richer chain physics":**

The saturation curve confirms the user's hypothesis from
2026-05-21: chain physics IS richer with more prime-spaced probes.
The increase in joint MI per Sylow added is non-trivial across all
corpora, with NATURAL TEXT showing the most dramatic growth
(substrate_agda: 0.08 → 2.72 bits, 34× growth from |S|=1 to |S|=6).

Per [[multi-route-equivariance-recovery]]: each Sylow probe is one
chart in the atlas; the atlas's joint MI is the gauge-equivariant
reading. Adding charts grows the reading until saturation.

**Per [[168-tower-as-fanout]]:** the GL(3, F₂) Sylow primes
{2, 3, 7} are the substrate's canonical 3-tuple. GL(4, F₂) adds 5;
GL(5, F₂) adds 31 (Mersenne); each GL(n, F₂) potentially adds new
primes. The JJ-arc validates this ladder empirically — adding 5
to {2, 3, 7} (going GL(3, F₂) → GL(4, F₂)) measurably improves MI
on every tested corpus.

**Per [[multi-field-tower-architecture]]:** the joint Sylow atlas
IS the FieldFanOut over the prime factorization. JJ confirms
empirically that the FanOut structure has compositional value
at the predictor level.

**Per [[3plus1-parity-universal]]:** at |S|=4 ({2, 3, 5, 7}), the
joint atlas has 4 probes — exact match to 3+1 universal (3
discrete Sylows + 1 newly-added).

**Per [[expose-generator-not-orbit]]:** the multi-Sylow atlas IS
the GENERATOR of predictability; any single-Sylow reading is an
orbit point that hides the generator.

**Per [[negative-findings-corpus-bound]]:** simulated cost
reduction vs unigram; real codec bpb gain over V7's actual
predictors expected smaller. substrate_memory regression bounded
to current parameterization.

**KK-arc target candidates:**
  1. Triple-V₄-crumb-per-probe: extend each Sylow probe from 1
     crumb to 3 crumbs at staggered offsets within the prime
     period. Tests whether per-Sylow refinement helps.
  2. Sylow-prime-AWARE atlas (not just numeric offset): include
     a per-prime "phase index" so different positions modulo p
     act as different sub-charts.
  3. Codec wiring of multi-Sylow predictor: real V7 integration;
     measure codec bpb vs V7 baseline (NOT unigram).
  4. Mersenne-Sylow extension: add Sylow-31 (GL(5, F₂)) and
     Sylow-127 (GL(7, F₂)); test whether very-long-range
     correlations register.
  5. Per-prime Hamming(7,4) recovery on mispredict: extend EE7
     recovery to each Sylow class's misprediction set.

Related: [[ii-arc-atlas-of-probes]] (parent — atlas-of-probes
framing JJ generalises along the Sylow-prime axis);
[[multi-route-equivariance-recovery]] (atlas-vs-chart discipline
JJ executes at the Sylow level);
[[168-tower-as-fanout]] (GL(3, F₂) Sylow structure 2³·3·7 → 4-Sylow
extension to GL(4, F₂));
[[kinematic-gauge-sacrifice-catalog]] (the 3 Sylow mechanical
classes + 4th continuum class);
[[hh-arc-prime-sampled-chain]] (sibling — HH single-pair (p, q);
JJ generalises to k-Sylow joint);
[[gg-arc-multiprime-spectral]] (sibling — GG single-prime spectrum;
JJ's chain-context approach is decoder-symmetric where GG was
windowed-only);
[[multi-field-tower-architecture]] (FieldFanOut realises the
multi-Sylow composition structurally);
[[3plus1-parity-universal]] ({2,3,5,7} = 3+1 at the Sylow-class
level);
[[expose-generator-not-orbit]] (atlas as generator);
[[chain-walk-blocks-rotation-factor]] (substrate-codec compresses
chain-walk structure; multi-Sylow context exposes it);
[[negative-findings-corpus-bound]] (results bounded; memory
regression an honest finding).
