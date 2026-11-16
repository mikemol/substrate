---
name: octonion-loop-expressivity-limit
description: "F₂ⁿ × F₂ at any scale covers only 2^(n+1) permutations of 2ⁿ bits — vanishing fraction of S_{2ⁿ}; user-expected operations like \"swap bits 6 and 7 specifically\" are NOT in the group; substrate codec needs richer permutation structure (Coxeter S_{2ⁿ}) for full bit-rearrangement expressivity"
metadata: 
  node_type: memory
  type: feedback
  originSessionId: bb094a39-05c5-494d-8b01-cc34809ccae9
---

Discovered while diagnosing BB-arc's failure to compound rotation
with backref+S₄.

**The structural limitation.**

The Cayley-Dickson F₂-octonion-loop at scale n is the group F₂ⁿ × F₂
(size 2^(n+1)). It acts on 2ⁿ-bit values by:
  1. XOR-k bit-position permutation (p → p ⊕ k).
  2. Optional chirality bit-flip (XOR with all-ones mask).

The XOR-k permutations are a VERY specific subset of S_{2ⁿ}: they
are involutions whose orbits are all pairs of bit positions related
by XOR. Composition is XOR-addition: applying XOR-k₁ then XOR-k₂ is
XOR-(k₁ ⊕ k₂), staying in the group.

Group sizes:

  scale n   bit-width   |F₂ⁿ × F₂|   |S_{2ⁿ}|    coverage
  n = 3     8           16          40320        0.04%
  n = 4     16          32          2.1 × 10¹³   1.5 × 10⁻¹²
  n = 5     32          64          2.6 × 10³⁵   2.4 × 10⁻³⁴

The expressivity VANISHES at higher scales.

**The user's expected operations are outside the group.**

  * "Swap bits 6 and 7 specifically (no other changes)" — this is
    the transposition (6, 7) ∈ S₈. F₂³ × F₂'s closest is k=1, which
    swaps (0,1), (2,3), (4,5), AND (6,7) all at once. The substrate
    can't isolate one pair-swap.

  * "Group bits 6-7 across 2-4 bytes" — at scale=4 (word, 16-bit),
    moving positions {6, 7, 14, 15} to be contiguous requires a
    permutation like σ = (6 12)(7 13)(14 14)(15 15). NOT an XOR-k
    permutation. F₂⁴ × F₂'s k=8 swaps the high byte and low byte
    bitwise but doesn't REARRANGE bits to be contiguous.

**The substrate-honest fix.**

Per [[v4-typeclass-architecture]]: V₄ goes through the Coxeter
framework. The same framework extends to S_{2ⁿ} via
adjacent-transposition generators:
  S_n = ⟨s_1, ..., s_{n-1} | sᵢ² = 1, sᵢsᵢ₊₁sᵢ = sᵢ₊₁sᵢsᵢ₊₁,
                              sᵢsⱼ = sⱼsᵢ for |i−j| ≥ 2⟩

Adjacent transpositions reach ALL of S_{2ⁿ}. A Coxeter word over
{s_1, ..., s_{2ⁿ-1}} encodes any bit permutation. Word length is
at most n(n−1)/2 = O(n²); typical bit reorganisations need much
shorter words.

The Coxeter-word emission opcode would be variable-length:
  S_BITPERM(s_i_1, s_i_2, ..., s_i_k)
emitted as a sequence of small integers (each ∈ [1, 2ⁿ−1]). The
adaptive predictor learns the most common generators are cheap.

This is the substrate-native path forward for richer bit-permutations.

**Why the BB-arc's F₂ⁿ × F₂ choice was the right starting point.**

  * It's the smallest non-trivial group at each scale (covers
    chirality + basic permutation axes).
  * It's the (3+1)-parity universal at every scale per
    [[3plus1-parity-universal]] — n permutation axes plus 1 chirality.
  * It composes well algebraically (abelian + involutive = simple).

But the empirical limitation makes it insufficient for the
compression task the user expected. The honest path forward is
Coxeter-word permutations OR a hybrid where F₂ⁿ × F₂ covers
common cases and Coxeter words extend to special cases.

**Diagnosis composability issue (separate from expressivity).**

Even if we had full S_{2ⁿ} expressivity, the byte-level rotation
× chain-level backref doesn't compound. Reason:

  * Byte rotation operates on input BEFORE chain walk.
  * Backref operates on chain content AFTER chain walk.
  * Chain walk is STATEFUL (chamber state = cumulative permutation
    of all prior nibbles). Different input bytes → different chain
    sequence in non-linear ways.
  * S₄ residue (backref's chain-level rotation) can compensate
    chamber-state DIFFERENCES but not arbitrary chain-sequence
    PERMUTATIONS.

Conclusion: the two rotations operate at structurally different
layers separated by a non-linear stateful transform. They do not
multiplicatively compose for compression.

**Substrate-honest path forward** (per [[two-path-commutativity]]):

The hidden 2-path is between (byte → rotate → chain walk → backref)
and (byte → chain walk → rotate-chain → backref). These are NOT
equivalent. To make rotations compose, EITHER:

  (a) Both rotations at the same layer (the AA-arc V₄/S₄ residue
      already does chain-layer; BB-arc's byte-layer rotation is the
      odd-one-out).
  (b) Define a chain-level analog of the byte rotation — i.e.,
      derive a chain-permutation from the byte rotation through
      the chain walk's structure. Mathematically non-trivial;
      requires understanding how byte-permutations factor through
      NIBBLE_TO_PERM composition.

The substrate's [[two-path-commutativity]] discipline says:
parametrizing one axis while enumerating another leaves a hidden
2-path; the fix is collapsing both axes through the generator.

The GENERATOR here is the chain walk itself: chain walk = sequence
of NIBBLE_TO_PERM compositions. Byte rotations don't factor
naturally through this composition.

**Implication for future arcs.**

The BB-arc's structural deliverable (the multiscale rotation
generator) is valid — it's a substrate-native primitive. But its
EMPIRICAL ROLE as a compression composition with chain-level
machinery is limited by FOUR compounding issues:

  (1) **Expressivity** — F₂ⁿ × F₂ is too small for arbitrary bit
      permutations.
  (2) **Composability** — byte-layer × chain-layer don't
      multiplicatively compose through the stateful chain walk.
  (3) **Estimator misalignment** — the BB6 byte-entropy estimator
      picks rotations that minimise BYTE distribution entropy, but
      the codec's cost is determined by CHAIN-SYMBOL distribution
      after the chain walk. The two are non-linearly related; a
      rotation that minimises byte entropy may maximise chain entropy.
  (4) **Per-block header overhead** — at block_size=64 on small
      corpora the rotation-table overhead (3 × num_blocks bytes) is
      5-10% of the corpus, dominating any gains.

Empirical from BB5+BB6 retest (4KB-ish corpora):

  corpus       identity   block-rot (BB6)   backref+S₄   both
  T1+T2        2.758      3.158 (R)         0.653 (best) 1.053
  memory_2KB   7.508      9.418 (R)         7.508 ≈ best 9.457

Block-rotation REGRESSES across the board even though the
empirical single-rotation sweep (BB7) found rotations that
modestly BENEFIT. The BB6 auto-discovery picks a different
rotation than the optimal one because byte-entropy != chain-entropy.

Future arc options:

  CC1. Coxeter-word S_{2ⁿ} permutations as a richer alternative.
       Closes expressivity (1).

  CC2. Chain-level analog of multiscale rotation. Find the chain-
       permutation derived from each (scale, k, f) and apply at
       the chain layer. Closes composability (2).

  CC3. Replace the chain walk with a STATELESS transform. Removes
       the composability issue entirely but loses the substrate's
       V₄ ⋊ S₃ chamber-walk structure. Probably too invasive.

  CC4. Embrace the limitation: the codec's rotation primitive is
       useful AS A STANDALONE compressor (single-rotation choice
       per stream, not composed). Document as such.
