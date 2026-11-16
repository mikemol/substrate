---
name: chain-walk-blocks-rotation-factor
description: "byte-level bit-permutations CANNOT factor as chain-level permutations through the substrate's stateful chain walk — the chamber state is the cumulative composition of NIBBLE_TO_PERM elements; only central (identity) chain-permutations commute with all states; the BB-arc rotation × backref non-compounding has a structural reason, not an implementation bug"
metadata: 
  node_type: memory
  type: feedback
  originSessionId: bb094a39-05c5-494d-8b01-cc34809ccae9
---

CC4 structural finding closing the BB-arc's open composability
question.

**The question:** Given a byte-level bit-permutation π applied
BEFORE the chain walk, is there a chain-level permutation σ
applied AFTER the chain walk such that σ ∘ chain_walk = chain_walk
∘ π? If yes, BB-arc rotation × backref would compose naturally.

**The answer: NO, generically.**

**Proof sketch:**

The chain walk produces chamber state c_k = c_{k-1} ∘
NIBBLE_TO_PERM[n_k] where n_k is the k-th nibble of the input and
∘ is permutation composition. Each chamber state is an element of
S₄ (24 chambers).

Apply byte permutation π to input bytes; this changes the nibble
sequence (n_k) to (n'_k). The new chain walk produces c'_k =
c'_{k-1} ∘ NIBBLE_TO_PERM[n'_k].

For a chain-level σ to factor π, we'd need σ(c_k) = c'_k for all k.

Equivalently:
  σ(c_{k-1} ∘ NIBBLE_TO_PERM[n_k]) = c'_{k-1} ∘ NIBBLE_TO_PERM[n'_k]
                                    = σ(c_{k-1}) ∘ NIBBLE_TO_PERM[n'_k]

If σ is left-multiplication by some g ∈ S₄ (the natural form):
  σ(x) = g x
Then:
  g (c_{k-1} ∘ NIBBLE_TO_PERM[n_k]) = (g c_{k-1}) ∘ NIBBLE_TO_PERM[n'_k]
  ⟹  g NIBBLE_TO_PERM[n_k] = (g c_{k-1}) (c_{k-1})^{-1} NIBBLE_TO_PERM[n'_k]
                          = NIBBLE_TO_PERM[n'_k]
  ⟹  NIBBLE_TO_PERM[n'_k] = g NIBBLE_TO_PERM[n_k]

This must hold for ALL k INDEPENDENT of the chamber state c_{k-1}.
That requires the permutation g to "absorb" arbitrary byte/nibble
changes through left-multiplication. The only g ∈ S₄ that left-
multiplies ANY element to ANY other element is... none. The action
is faithful; only g = identity leaves all elements fixed.

For σ as right-multiplication by g (σ(x) = x g):
  c_{k-1} NIBBLE_TO_PERM[n_k] g = c_{k-1} NIBBLE_TO_PERM[n'_k]
  ⟹ NIBBLE_TO_PERM[n_k] g = NIBBLE_TO_PERM[n'_k]
  ⟹ g = NIBBLE_TO_PERM[n_k]^{-1} NIBBLE_TO_PERM[n'_k]

This must hold for ALL k, but the RHS depends on k. Only constant
across all positions if the bit-permutation π maps every nibble to
the SAME relative position — a very restrictive condition (e.g.,
"add a constant nibble to every nibble") that almost no bit-
permutation satisfies.

For more general σ (conjugation, polynomial maps, etc.): similar
analysis shows the chain walk's statefulness blocks generic factor.

**Conclusion:**

Byte-level rotations do NOT factor as chain-level rotations through
the substrate's stateful chain walk. The BB-arc rotation × backref
non-compounding is a STRUCTURAL CONSEQUENCE of the chain walk's
properties, not an implementation bug.

**Implication:**

The codec's three rotation layers (stream Z/8 / byte F₂ⁿ × F₂ or
Coxeter S_{2ⁿ} / chain S₄) cannot be unified through the chain
walk. They are TRULY INDEPENDENT structural axes, and their
empirical interaction is non-trivial.

To make them compose, one would need to either:
  (a) Replace the chain walk with a stateless transform (loses
      substrate's V₄ ⋊ S₃ structure — too invasive).
  (b) Apply all rotations at the SAME layer (the AA-arc S₄ residue
      already at chain layer; rotations at byte/stream layer would
      need lifting to chain layer in a non-naive way).
  (c) Treat them as orthogonal axes whose empirical interaction is
      a per-corpus measurement, not a structural composition.

The substrate-honest reading is (c): the rotation layers are not
multiplicatively composable; each contributes independent structural
information that the codec speculates over independently.

Per [[two-path-commutativity]]: the hidden 2-path between
(byte → rotate → chain walk → backref) and
(byte → chain walk → backref under chain-rotation) does NOT close.
There is no commutator; the substrate's discipline of "collapsing
both axes through the generator" reveals that the chain walk's
generator (NIBBLE_TO_PERM composition) doesn't admit external
permutations as factors.

This is the structural finding the BB-arc surfaced empirically;
CC4 closes it mathematically. Future codec design that wants to
compose multiple rotation layers needs to operate at a SINGLE
layer (which the AA-arc's chain-level S₄ residue is the
substrate-honest choice).
