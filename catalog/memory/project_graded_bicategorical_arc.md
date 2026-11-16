---
name: project-graded-bicategorical-arc
description: "After the 10-slice 2-D word algebra arc completes, the next arc is \"graded structures via FreeCyclic + DirectProduct\" — surfacing the substrate's bicategorical / strict n-monoid infrastructure that the Coxeter framework already implicitly carries."
metadata: 
  node_type: memory
  type: project
  originSessionId: 28a7490c-cf4a-4933-8773-215362d96f13
---

**STATUS (updated): LARGELY REALIZED — no longer "queued."** The strict
arc is CLOSED (`Category.GradedBicategorical` with `Strict2Monoid`,
`Strict2Monoid.FromCoxeter`, the V₄ instance, `DirectProduct`); `GradedMonoid`
is instantiated (`Groups.FreeCyclic-Coxeter-GradedMonoid`, `vec-flat-monoid`).
Deliverables 1–3 below = done. The missing graded MORPHISM + graded
ADJUNCTION connectors were added in the Dent Track-A unification
(`Algebra.Wedge.Graded.{Morphism,Adjunction,MonoidalAdjunction}`; see
[[project_dent_system]]). Remaining genuinely-open: deliverables 4–5
(H²(G;A) as graded, the cocycle/3+1/torsion ties) and the weak-2-monoid /
multi-object follow-ons in the caveats.

After the current 10-slice 2-D word algebra arc (FreeCyclic-Coxeter,
Z3-x-FreeCyclic, Z4-x-FreeCyclic, phase-projections, etc.) lands,
the queued NEXT arc is:

**Graded structures via FreeCyclic + DirectProduct**, surfacing the
substrate's bicategorical / strict n-monoid infrastructure that the
Coxeter framework already implicitly carries.

**Why:** The Coxeter Core's (Word, ++, _≈_) structure IS a 1-object
strict 2-monoid:
* 0-cells: single object.
* 1-cells: Word Gen.
* 2-cells: _≈_ (= normalize w₁ ≡ normalize w₂).
* Vertical comp: trans on the underlying _≡_.
* Horizontal comp: _·_ = normalize ∘ ++.
* Associativity strict on ++; weakened to ≈ on _·_.

FreeCyclic-Length added ℕ-grading on 1-cells (insert-as-suc-length
makes insert ≡ suc at the length level). With DirectProduct, the
1-cells become ℕ-indexed; the composition tracks degree. This is
enrichment over ℕ — a "graded bicategory."

Nested DirectProduct gives strict n-monoids (= 1-object strict
n-categories) for free: each new axis is a Coxeter instance + the
existing DirectProduct combinator.

**How to apply:** When the user asks for "the next arc" after the
current 2-D work, propose this graded-structures direction. The
deliverables:
1. Name the strict 2-monoid structure that Coxeter Core already
   carries: a record `Strict2Monoid` packaging Word/_·_/_≈_ as
   the 1-cell/horizontal-comp/2-cell of a 2-monoid.
2. Surface FreeCyclic as the canonical "ℕ-grading axis."
3. Build a few graded instances: Z/n graded by ℕ, V₄ graded by ℕ.
4. Identify the cocycle group H²(G; A) as itself naturally graded.
5. Connect to substrate themes: 3+1 parity universal as
   degree-1 cocycle; torsion-element universal as element-order =
   grading degree.

**Caveats / honest scope:**
* Multi-object bicategories (non-trivial 0-cells) need different
  framing — `Word` over typed generators or directed graphs.
* Strict vs weak: substrate has weak via _≈_; strict ++-assoc + weak
  _·_-assoc is the natural setting.
* Coherence diagrams (pentagon, triangle) need explicit verification
  per instance; substrate has normalize-triple/quad/quint which may
  cover the FreeCyclic-grading direction's coherences.

**Bigger payoff:**
FreeCyclic isn't bookkeeping for Z/n — it's the substrate's grading
infrastructure. The bicategorical / higher-categorical structure
follows from there, opening:
* Cohomology degree as a first-class concept.
* Cocycles as graded objects.
* Higher cells (3-cells, ...) via nested DirectProduct.

Reference: this arc was queued in the same session where the
2-D word algebra arc was launched. The user observed
"FreeCyclicCoexeterLength upgrade gives us the word-algebra-level
richness to get bicategories for ~free" — this memory captures
that intuition for the future arc.
