---
name: project-cycle-generator-as-2-cocycle
description: "The cycle generator in the substrate's 2-D word algebra (FreeCyclic × Zₙ) plays the role of a 2-cocycle in group cohomology — concretely realising the substrate's homology/cohomology recursion theme at the Coxeter level."
metadata: 
  node_type: memory
  type: project
  originSessionId: 28a7490c-cf4a-4933-8773-215362d96f13
---

The cycle generator (FreeCyclic-Coxeter's single generator `a`,
representing ℕ) in the substrate's 2-D word algebra construction
(`Zₙ-x-FreeCyclic` modules) plays the role of a **2-cocycle in
group cohomology**.

**The structural mapping:**

* The 1-D Coxeter group Zₙ has H²(Zₙ; A) classifying central
  extensions of Zₙ by A. For A = ℤ (or ℕ at the monoid level), the
  cycle-counter generator IS a representative of the non-trivial
  class.
* Concretely: the 2-D word algebra Zₙ × FreeCyclic represents the
  universal cover ℕ → Z/n; the cycle generator counts "how many
  wraps" — that's exactly the cocycle data of the extension.
* The phase-projection `(w-p, w-c) → w-p` FORGETS the cocycle,
  reducing to the base group Zₙ.
* The cycle-projection (= proj₂) EXTRACTS the cocycle data.

**Z/4 vs V₄ as cohomology class distinction (recorded for future
cocycle-theory work):**

* Z/4 sits in the non-split extension `1 → Z/2 → Z/4 → Z/2 → 1`.
* V₄ sits in the SPLIT extension `1 → Z/2 → V₄ → Z/2 → 1`.
* Both are classified by H²(Z/2; Z/2) = Z/2:
  * Trivial class (= 0 ∈ Z/2): gives V₄ (direct product).
  * Non-trivial class (= 1 ∈ Z/2): gives Z/4 (cyclic).
* Substrate has V₄ via V4-as-Z2xZ2 (= Z₂ × Z₂ direct product); Z/4
  via Z4-Coxeter (= cyclic Coxeter). The cohomological distinction
  is implicit; making it explicit would require formalising
  H²(Z/2; Z/2) and identifying the two extension classes via the
  substrate's 2-cocycle machinery.

**How to apply (when relevant):**

* When a substrate site has "two adjacent cyclic structures with
  potentially different binding (split vs non-split)", recognise this
  as a cohomology-class distinction. Examples:
  * V₄ vs Z/4 (above).
  * Direct products vs semidirect products (substrate has
    SemidirectProductGroup for the latter).
  * Trivial cocycle vs non-trivial cocycle in cohomology.
* The 2-D word algebra (FreeCyclic × Coxeter) IS the substrate's
  cocycle-bookkeeping device. The cycle component IS the cocycle.

**Connections:**

* [[project-homology-cohomology-recursion]]: this memory makes one
  level of the recursion concrete (cycle counter = cocycle).
* [[project-3plus1-parity-universal]]: the +1 chirality at each
  level often plays a cocycle-counter role; making this explicit at
  the substrate level connects.
* [[project-graded-bicategorical-arc]]: the next arc (graded
  structures) elevates the cycle counter to a degree-grading, which
  is the natural cohomology-as-graded-cohomology connection.
* [[project-composite-torsion-euler-substrate]]: composite-order
  Lagrange ↔ CRT decomposition needs cocycle theory for non-coprime
  prime-power components.

**Status:** identified, named, documented. Concrete formalisation of
H²(Z/2; Z/2) as a substrate construction is a future arc — touching
this only when a use site demands.
