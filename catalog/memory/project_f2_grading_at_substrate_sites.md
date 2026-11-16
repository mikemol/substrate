---
name: project-f2-grading-at-substrate-sites
description: "Catalogue of F₂-graded monoid structures across the substrate (V₄'s three gradings; Bivector's weight-parity; etc.) and how they relate to (but are NOT identical to) the 3+1 parity universal carrier-set decomposition."
metadata: 
  node_type: memory
  type: project
  originSessionId: 28a7490c-cf4a-4933-8773-215362d96f13
---

The substrate's F₂-grading arc (Arc 2 of the 20-slice plan that
introduced RGradedMonoid + F₂-CommMonoid) produced multiple
F₂-graded instances. This memory catalogues them and the structural
relationships.

**F₂-graded instances:**

1. **V₄-Coxeter-F2Graded** (length-parity): degree = parity of word
   length. Splits V₄ as {ε, AB} (degree 𝟘) vs {A, B} (degree 𝟙).

2. **V₄-Coxeter-F2Graded-CountA** (count-A-parity): degree = parity
   of count-of-A. Splits V₄ as {ε, B} vs {A, AB}.

3. **V₄-Coxeter-F2Graded-CountB** (count-B-parity): degree = parity
   of count-of-B. Splits V₄ as {ε, A} vs {B, AB}.

4. **Bivector-F2Graded** (weight-parity): degree = XOR of all 6
   entries. Splits Bivector as even-weight vs odd-weight (the
   standard binary-code parity).

**Structural relations:**

* On V₄: length-parity = count-A-parity + count-B-parity (in F₂).
  Every generator is either A or B, so length = count-A + count-B
  at the ℕ level; passing through parity preserves the relation.
* The pair (count-A-parity, count-B-parity) gives the coordinate
  iso V₄ ≅ Z/2 × Z/2 as a pair of F₂-graded monoid homomorphisms.

**Correction to [[project-3plus1-as-graded-cocycle]]:**

The earlier framing treated the 3+1 parity universal as a single
F₂-grading. This Arc 2 work showed that's OVERSPECIFIED:

* The 3+1 universal is a CARRIER-SET DECOMPOSITION (V₄-Nonzero +
  identity; 3 collinear + 1 chirality at Fano; etc.) — NOT a monoid
  grading.
* The CARRIER-SET DECOMPOSITION is not a monoid homomorphism because
  V₄-Nonzero etc. are NOT CLOSED UNDER · (e.g., A · A = ε ∈ identity,
  not in Nonzero).
* The F₂-grading framework captures parity-style invariants (length,
  count-A, weight) that ARE monoid homomorphisms — but they differ
  from the 3+1 carrier-set split.

The 3+1 universal is therefore better understood as a SET-LEVEL
property (a distinguished subset + complement) accompanied by a
SEPARATE PARITY-INDICATOR FUNCTION that may or may not be a monoid
homomorphism.

**How to apply:**

When the substrate exhibits a 3+1 split at a site, ask:
1. Is the "3" subset closed under the relevant composition? If yes,
   it might be a SUBGROUP (and the 3+1 might be a coset
   decomposition).
2. Is there a PARITY function from elements to F₂ that respects
   composition? If yes, this is the F₂-graded structure
   (RGradedMonoid F₂-CommMonoid).
3. Is the parity function the SAME as the 3-vs-1 indicator? If yes,
   the 3+1 and the parity coincide. If no, they're independent
   structural features.

For V₄: the 3-Nonzero subset is NOT closed under ·; the three
F₂-gradings (length/A/B-parity) don't coincide with the 3+1 indicator.
The 3+1 is set-level; the gradings are monoid-level.

**Substrate-wide implication:**

The substrate has F₂-graded structures at:
* All Coxeter Word algebras (length-parity grading on any Word A).
* All count-of-generator parities (one grading per generator type).
* Bivector via weight-parity (and analogs for any Vec F₂ n).
* Future: BilinForm n with determinant-mod-2 parity? Codes with
  syndrome-parity? Each is a candidate F₂-graded instance.

**Connections:**

* [[project-3plus1-parity-universal]]: the carrier-set phenomenon.
* [[project-cycle-generator-as-2-cocycle]]: cocycle = degree-shift
  generator; in F₂-graded form, degree shifts via F₂ addition.
* [[project-graded-bicategorical-arc]]: ℕ-graded GradedMonoid
  generalizes to RGradedMonoid for any R.
* [[feedback-categorical-name-first]]: "F₂-grading" is the categorical
  name for what was previously "parity invariant" or "chirality F₂."
