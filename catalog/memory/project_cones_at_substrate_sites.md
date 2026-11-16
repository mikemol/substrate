---
name: project-cones-at-substrate-sites
description: "Catalogue of Cone / Cone.WithMorphisms instances at concrete substrate sites. HodgeStar's ★-fixed subspace IS the (2-base, 1-morphism) Cone.WithMorphisms instance (= Equalizer-Of (apply hodge-star) id). Each substrate \"+1 witness\" pattern fits a specific cone shape."
metadata: 
  node_type: memory
  type: project
  originSessionId: 28a7490c-cf4a-4933-8773-215362d96f13
---

After the Cone primitive family lands (Substrate.Category.Cone +
Cone.WithMorphisms + Cone.EdgeApex + Cone.FieldFilling), the
substrate's structural patterns can be CONCRETELY REALIZED as cone
instances. Landed worked examples:

**Discrete-base cones (no morphisms in base):**

* `Cone-V4-3plus1` — V₄ as (3,1)-shape cone (3 readings + 1 apex
  witness, filling 2²).
* `Cone-Hamming-7plus1` — Hamming(8,7) as (7,1)-shape cone (filling 2³).
* `Cone-HodgeStar-EdgeApex` — Hodge ★ as edge-apex over trivial base.

**WithMorphisms-base cones (base morphisms first-class):**

* `Cone.EqualizerWithMorphisms` — generic Equalizer pattern.
* `Cone.PullbackWithMorphisms` — generic Pullback pattern.
* `HodgeStar-ConeWithMorphisms` — Hodge ★ as a ConeWithMorphisms
  instance characterising the self-dual subspace. The cone IS
  Equalizer-Of (apply hodge-star) id, realised via WithMorphisms.

**Patterns to surface as cone instances (deferred):**

* Fano line as (3,1)-cone (3 collinear points + complement witness).
* SelfDual sd-pair-* as (3,1)-cones at the dim-4 antisymmetric
  subspace.
* dim-3 ↔ dim-4 SymBilinForm bridge as a multi-leg cone.
* ReservedBridge's 168-gauge family as cones with bond-tower bases.
* V₄-Nonzero subset stabilisers as cones with chirality apex.

**How to apply:**

When the substrate observes a "structure + projection / readings"
pattern, recognise as cone:

1. **Count the readings** (= base cardinality M).
2. **Identify the witness** (= apex; 1 if single object, or an edge
   if it's a morphism, or N if multiple).
3. **Check for base morphisms** (parallel pair → Equalizer cone;
   cospan → Pullback cone; etc.).
4. **Determine the field filling** (M + N = p^k for prime p).
5. **Instantiate Cone or Cone.WithMorphisms accordingly**.

**Connections:**

* [[project-3plus1-is-cone-instance]] — 3+1 universal as cone
  framing.
* [[project-cone-subsumes-equalizer-pullback]] — Equalizer/Pullback
  as specific cone shapes.
* [[project-freelinearization-substrate-sites]] — sister project at
  the FreeLinearization level.

**Status:** primitives + 5 worked instances landed. Future arcs can
add more concrete instances as substrate sites become available.
