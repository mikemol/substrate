---
name: project-freelinearization-substrate-sites
description: "The substrate's existing F₂-linear maps (HodgeStar, basis-permutation-Linear instances, bivector bridges, etc.) inherit the FreeLinearization (#6) universal property via free-linearize. Two worked examples landed (HodgeStar, Cycle3); many more follow the same pattern."
metadata: 
  node_type: memory
  type: project
  originSessionId: 28a7490c-cf4a-4933-8773-215362d96f13
---

After the FreeLinearization arc, the substrate's existing F₂-linear
maps (any constructed via `linear-from-images`) inherit the
FreeLinearization universal property via the `free-linearize`
constructor.

**Worked examples (landed):**

* `Substrate.Algebra.F2.HodgeDim4.HodgeStar-FreeLinearization`
  — Hodge ★ at dim 4 as FreeLinearization 6 6.
* `Substrate.Algebra.F2.Linear.FromImages.Permutation.Cycle3-FreeLinearization`
  — basis-permutation-Linear σ₃ as FreeLinearization 3 3.

**Available follow-ons (mechanical):**

Any substrate site that uses `linear-from-images` can wrap as a
FreeLinearization instance:

* Cycle4-FreeLin, Cycle5-FreeLin — mirror Cycle3 at n=4, 5.
* basis-permutation-Linear σ at any σ : Fin n → Fin n — generic
  pattern.
* Image-Equivalent / apply-Selector-style uses in Codes work
  (per [[feedback-universal-property-discipline]]).
* TensorProduct.pair (for fixed argument) as FreeLinearization at
  the curried bilinear.

**How to apply:**

When the substrate has `linear-from-images f` for some
`f : Fin n → Vector m`, the FreeLinearization wrapper is:
```agda
my-FreeLin : FreeLinearization n m
my-FreeLin = free-linearize f
```
One line. The wrapper provides the four record fields: images,
extension, extension-on-basis, uniqueness.

**Why surface this:**

* Naming makes the categorical content explicit at the use site.
* Downstream code can cite FreeLinearization's uniqueness instead
  of re-deriving via linear-extensionality.
* Future cross-substrate retrofit (replacing linear-from-images with
  FreeLinearization.extension at downstream sites) is mechanical.

**Status:** primitive + 2 worked instances landed. Substrate-wide
retrofit (citing FreeLinearization instead of linear-from-images at
all current sites) is a follow-on; mostly mechanical, low priority
unless a use site demands.

**Connections:**

* [[project-freelinearization-names-linear-from-images]] — the
  primitive's intent.
* [[feedback-universal-property-discipline]] — the substrate's
  linear-from-images discipline that FreeLinearization names.
* [[feedback-composable-primitives-over-flat-enumeration]] — the
  composable-primitive pattern that FreeLinearization realizes.
