---
name: reserved-selfdual-bijection-gauge
description: "The Codeword.Reserved ↔ SelfDual bijection from M-11.dim4.codeword-bridge is ONE of 168 F₂-linear choices. No F₂-linear bijection is V₄-equivariant (the two V₄ actions don't match). Treat the bijection as a gauge choice; surface alternatives when consumers depend on it."
metadata: 
  node_type: memory
  type: project
  originSessionId: 28a7490c-cf4a-4933-8773-215362d96f13
---

**Fact.** The bijection `Codeword.Reserved ↔ SelfDual` established by M-11.dim4.codeword-bridge (via `Vector 3` pivot) is **one of 168 F₂-linear choices**. Both sides are 3-dim F₂-subspaces; any F₂-linear bijection between them is a GL(3, F₂) element (order 168).

**Why:** Future consumers of the bridge may rigidify on the specific bit ↔ self-dual-coefficient assignment ours uses. Per `feedback_choice_rigidification_in_substrate` and `feedback_ordering_is_chirality_choice`: don't let a gauge choice freeze into THE canonical without acknowledging the 168-element gauge freedom.

**How to apply:** When extending the bridge (e.g., proving downstream properties), check whether the property depends on the specific bijection or is gauge-invariant. If gauge-dependent, surface the alternative bijections and let the user/catalog choose. The file `Substrate.Algebra.F2.HodgeDim4.ReservedBridgeAlternatives` formalises 2 of the 168 alternatives concretely; others can be added as needed.

## Coset structure

| Bijection type | Count | Subgroup interpretation |
|----------------|-------|------------------------|
| F₂-linear | 168 | GL(3, F₂) |
| F₂-affine (linear + translation) | 1,344 | F₂³ ⋊ GL(3, F₂) |
| All set-level | 40,320 | S₈ |

Within F₂-linear:
- **Basis permutations** (6 = 3! = |S₃|): permute which bit ↔ which sd-pair generator.
- **Non-permutation linear** (162 = 168 − 6): use non-basis self-dual elements (sums of generators).

## V₄ action analysis (corrected — sacrifice-ladder)

The V₄ action on Reserved is the **regular representation on axes** (V₄ = F₂² acts additively on the 4 axes; free transitive action; sign bit untouched). The V₄ action on SelfDual via partition-permutation is **V₄ ⊂ S₄ as the kernel of S₄ → S₃ on partitions** (trivial on the 3 sd-pairs).

These two actions have **incompatible orbit structures** (Reserved: 2 orbits of 4; SelfDual under partition-V₄: 8 orbits of 1). **Within the constraints (F₂-linear, this V₄ choice, bijective, cardinality 8-to-8), no V₄-equivariant bijection exists.**

**Sacrifice ladder.** V₄-equivariance is achievable by sacrificing a degree of freedom. Each sacrifice trades a rigidity for an enrichment (analogous to Cayley-Dickson, where each ladder step trades an algebraic law for richer structure):

| Sacrifice | What's lost | Recovery |
|-----------|-------------|----------|
| F₂-linearity | linear-structure constraint | F₂-affine V₄ ⊂ Aff(3, F₂) acts freely on F₂³ (2 orbits of 4); matches Reserved |
| V₄ subgroup choice | "natural" partition-V₄ | use a different V₄ ⊂ GL(4, F₂); some give non-trivial orbits on SelfDual |
| Cardinality (quotient by V₄) | F₂³ structure (8 → 2) | Reserved/V₄ ≅ {sign₀, sign₁} ≅ any 1-dim self-dual subspace |
| Bijectivity | 1-1 correspondence | many-to-one V₄-equivariant collapse |
| Embedding domain | "into SelfDual" | lift both sides to a larger F₂-space with V₄-equivariance |

**Meta-symmetry.** The choice of which sacrifice to make is itself a gauge / coset. Following the fractal pattern: 3 "primary" sacrifice axes (e.g., linearity / V₄-choice / bijectivity) + 1 null (= "no sacrifice, accept non-equivariance") instantiate **another F₂² Klein four** at the sacrifice-choice meta-level. The recursion continues upward.

**Zero-annihilation framing.** "Sacrifice a DOF" = multiply it by 𝟘 = annihilate it. Each sacrifice collapses one degree of freedom to recover equivariance in another. This mirrors the Cayley-Dickson ladder where ℂ → ℍ annihilates commutativity, ℍ → 𝕆 annihilates associativity, 𝕆 → 𝕊 annihilates alternativity — each annihilation IS a "zero multiplied into an algebraic law."

**The previous claim "no F₂-linear bijection is V₄-equivariant" is correct WITHIN ITS PREMISES** (F₂-linear + that specific V₄ + bijective). The PREMISES themselves are gauge choices, and other premises admit equivariance.

## Specific alternative bijections (formalised in ReservedBridgeAlternatives)

- **Canonical** (default, from M-11.dim4.reserved-bridge): bit i ↔ sd-pair generator i, identity permutation.
- **Cyclic shift** (alt A): bit 0 ↔ sd-pair-02-13, bit 1 ↔ sd-pair-03-12, bit 2 ↔ sd-pair-01-23. Demonstrates that 3-cycle permutations are also valid bijections.
- **Last-two swap** (alt B): bit 0 ↔ sd-pair-01-23, bit 1 ↔ sd-pair-03-12, bit 2 ↔ sd-pair-02-13. Demonstrates that transpositions on the sign vs axis bit choice are also valid.

All three are F₂-linear and pass the same kind of round-trip proofs. The catalog has no preferred choice among them at the F₂-linear level.

## Fractal recurrence at the meta-level

The space of "which alignment axis to prefer" is itself an instance of the **3+1 parity universal pattern** (see [[project_3plus1_parity_universal]]). Sample axes considered:

| Alignment axis | Role in gauge-freedom space |
|----------------|-----------------------------|
| coordinate-aligned (bit i ↔ sd-pair i) | V4-Nonzero element 1 |
| Hodge-axis-aligned (axis k ↔ sd-pair-(0,k)-comp) | V4-Nonzero element 2 |
| orbit-respecting (preserves S₃ action on 3 sd-pairs) | V4-Nonzero element 3 |
| **null / no preference** (any of 168 bijections equally) | **Identity = chirality dual** |

So the gauge-freedom space has THE SAME F₂² Klein four / F₂³ Hodge structure that the underlying Reserved and SelfDual spaces have. **The recurrence goes all the way to the meta-level.**

**Implication:** there is no "right" alignment axis at the gauge level — they're S₃-equivalent. The catalog should EXPOSE the 168-coset gauge freedom rather than fix one alignment axis. Rigidifying on a single axis at the gauge-choice level is gauge-rigidification at the meta-level (same anti-pattern as ordering-is-chirality-choice at the object level).

**Cross-references:** [[feedback_choice_rigidification_in_substrate]], [[feedback_ordering_is_chirality_choice]], [[feedback_multi_reading_ambient_discipline]], [[project_3plus1_parity_universal]].

## Categorical realization (added after Cone+Bond arc)

The 168-gauge has now been categorically anchored:

* **FieldFanOut representation** ([[project_168_tower_as_fanout]]):
  168 = 2³·3·7 realizes as FieldFanOut 3 with source Z/168 and
  targets (F₂³, F₃, F₇). Sketched in
  `Substrate.Algebra.PrimeFactor-168-FieldFanOut` (placeholder bonds).

* **Sacrifice ladder ↔ FanOut gauge choice**: each rung of the
  sacrifice ladder (F₂-linearity / V₄-subgroup-choice / bijectivity
  / cardinality) corresponds to a different way of USING the
  FieldFanOut structure — flatten to a specific chain (FieldTower),
  drop a target field, etc. The 168-gauge family lives at the
  meta-level above these specific sacrifices.

* **Per [[project_3plus1_is_cone_instance]] bond extension**:
  168 isn't a prime power, so the substrate's structural reading
  REQUIRES multi-field bonds. The FanOut is the substrate-native
  realization.

Categorical primitives now framing this gauge: `FieldFanOut` (#12),
`FieldTower` (#11), `FieldBond` (#10).
