---
name: project-cone-subsumes-equalizer-pullback
description: "The substrate's Cone primitive (#9) subsumes the older Equalizer (#2) and Pullback (#3) primitives as specific cone-shape instances; both are now realised as Cone instances with extra equalizer/pullback witnesses in the Σ-subtype apex."
metadata: 
  node_type: memory
  type: project
  originSessionId: 28a7490c-cf4a-4933-8773-215362d96f13
---

The substrate's `Substrate.Category.Cone` primitive (#9) subsumes
the older Equalizer (#2) and Pullback (#3) primitives as specific
cone shapes:

* **Equalizer** = (2, 1)-shape Cone: 2 base objects A, B + apex
  Equalizer-Of f g. The parallel-pair morphisms f, g : A → B aren't
  first-class in the discrete Cone, but the equalizer condition
  (f ∘ leg-A ≡ g ∘ leg-A) is implicit in Equalizer-Of's Σ-witness.
  Realized in [Substrate.Category.Cone.EqualizerInstance](agda/Substrate/Category/Cone/EqualizerInstance.agda).
* **Pullback** = (3, 1)-shape Cone: 3 base objects A, B, C + apex
  Pullback-Of f g. The cospan f : A → C, g : B → C is implicit;
  pullback condition (f ∘ π₁ ≡ g ∘ π₂) in Pullback-Of's witness.
  Realized in [Substrate.Category.Cone.PullbackInstance](agda/Substrate/Category/Cone/PullbackInstance.agda).

**What this means structurally:**

* The substrate's earliest categorical primitives (#2 Equalizer, #3
  Pullback) were specific cone shapes; the #9 Cone primitive is the
  general framework they fit into.
* The 3+1 parity universal at V₄ (per
  [[project-3plus1-is-cone-instance]]) is the (3, 1)-shape Cone
  instance — same generality level as Equalizer/Pullback but at a
  different base cardinality.
* Adding more primitives in the Cone family (e.g., (4, 1)-cone,
  (5, 2)-cone with bonds, etc.) is mechanical once the Cone primitive
  exists.

**Current limitation: discrete Cone.**

The substrate's Cone primitive doesn't track morphisms between base
objects. Equalizer's parallel pair (f, g : A → B) and Pullback's
cospan (f : A → C, g : B → C) are STRUCTURAL features that live in
the Σ-witness of Equalizer-Of / Pullback-Of, not in the Cone itself.

A `Cone.WithMorphisms` extension would add base-internal morphisms
+ leg-commutativity constraints, making the parallel pair / cospan
first-class. Deferred.

**How to apply:**

When the substrate observes a "diagram with apex and projections,"
recognise it as a Cone instance. The specific shape (parallel pair,
cospan, discrete, 3+1, etc.) determines which Cone subtype it falls
into:

* Equalizer = 2-base parallel pair.
* Pullback = 3-base cospan.
* Product = N-base discrete.
* 3+1 cone = 3-base with witness apex.

**Connections:**

* [[project-3plus1-is-cone-instance]]: the 3+1 universal as Cone
  framework.
* [[feedback-categorical-name-first]]: Cone is the categorical
  name; the substrate's older "kernel-of-(f,g)" / "orbit-
  intersection-fiber" naming becomes "Cone over (parallel pair)"
  / "Cone over (cospan)" at the categorical level.

**Status:** subsumption realised at the type level. Equalizer (#2)
and Pullback (#3) remain as named primitives for ergonomics; the
Cone instance modules provide the framework-level connection.
