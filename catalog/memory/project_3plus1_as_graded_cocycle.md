---
name: project-3plus1-as-graded-cocycle
description: "The substrate's 3+1 parity universal (V₄-Nonzero + chirality, Fano + complement, etc.) IS a degree-1 graded cocycle in the GradedMonoid + cycle-generator framework — connecting [[project-3plus1-parity-universal]] to [[project-cycle-generator-as-2-cocycle]]."
metadata: 
  node_type: memory
  type: project
  originSessionId: 28a7490c-cf4a-4933-8773-215362d96f13
---

The substrate's 3+1 parity universal (per
[[project-3plus1-parity-universal]]) is a SPECIFIC INSTANCE of the
graded cocycle structure named in [[project-cycle-generator-as-2-cocycle]]:

**The mapping:**

* Underlying group / 1-cells: the "3" part (V₄-Nonzero at the
  V₄-action site; the 3 non-zero elements of Fano at the Fano site;
  the 3 sd-pair-* at SelfDual; etc.).
* Cycle generator / 2-cocycle: the "+1" chirality (F₂ index that
  picks one of the two parity-orbits).
* Degree: 0 for elements in the underlying-group orbit, 1 for the
  chirality element.
* Compose property: combining a degree-0 with a degree-1 element
  yields degree-1; combining two degree-0 or two degree-1 elements
  yields degree-0 (= the parity addition).

**Concretely at V₄:**

* V₄-Nonzero = {a, b, c} (= 3 elements; degree 0).
* Chirality = ε vs the full-product (= 1 element flipping parity).
* The graded structure: degree(a) = degree(b) = degree(c) = 0;
  degree(chirality) = 1.
* Composition (V₄'s · operation) preserves degree-parity: deg(x·y)
  = deg(x) + deg(y) mod 2 — exactly the F₂-grading.

**Concretely at Fano (PG(2, 2)):**

* 7 points decompose as 3 collinear triples + 1 "complement"
  generator at each line. Each line is 3+1.
* Per line, the 3 collinear points span a 2-dim F₂ subspace; the
  complement is the parity-flipping element outside that subspace.
* The graded reading: collinear points are degree 0; complement is
  degree 1.

**Concretely at SelfDual (dim 4 Bivectors):**

* 3 self-dual sd-pairs (sd-pair-01-23, sd-pair-02-13, sd-pair-03-12)
  span the 3-dim self-dual subspace; degree 0.
* The chirality F₂ acts via Hodge ★ at each level; degree 1
  represents the "anti-self-dual" axis (which at F₂ collapses but
  carries the parity).

**Why this matters:**

Until now the 3+1 parity universal was a substrate-observed phenomenon
without a categorical name. The graded-monoid + cocycle reading
provides that name:

> The 3+1 parity universal IS a degree-1 cocycle in the substrate's
> GradedMonoid framework, with grading by Z/2 (= F₂ parity) rather
> than by ℕ (which FreeCyclic provides for the cyclic-cover case).

This unifies several substrate themes:
* [[project-3plus1-parity-universal]]: the phenomenon.
* [[project-cycle-generator-as-2-cocycle]]: the cocycle reading.
* [[project-graded-bicategorical-arc]]: the categorical handle.
* [[project-torsion-element-universal]]: the chirality element IS
  a torsion element (order 2 = F₂-parity).
* [[project-tetrative-metacircularity]]: at each meta-level, the
  3+1 reappears as a degree-1 cocycle.

**Concrete substrate implication:**

A "graded V₄" instance would package V₄-Nonzero (degree 0) + chirality
(degree 1) as a graded-monoid in the Z/2-grading. The substrate's
Z₂-grading version of GradedMonoid would generalize the ℕ-grading
to any commutative monoid R (here R = F₂ = Z/2).

**Status:** identified and named. Concrete F₂-graded GradedMonoid
implementation is a future arc (would build R-graded version of
GradedMonoid + V₄-as-Z2-graded instance).

**Connections to retire / clarify:**

Earlier work treated the 3+1 split as a "two-axis ambient cotype"
(per [[feedback-multi-reading-ambient-discipline]]). The cocycle
framing is more PRECISE: the two readings (3-collinear vs 1-chirality)
are the two cohomology classes in H¹(M; F₂) where M is the underlying
3-element structure. The ambient cotype is the cohomology group;
each reading picks a representative.
