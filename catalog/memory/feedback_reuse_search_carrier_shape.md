---
name: feedback_reuse_search_carrier_shape
description: "Re-expressing an Obj→Obj→Set₁ structure? Search the tower for its GRADED-CARRIER form (C:ℕ→Set + fold), not a same-shape quiver — the free object is usually LehmerPath/⊕-over, not a bespoke category to build."
metadata: 
  node_type: memory
  type: feedback
  originSessionId: d35bc15a-16b8-42c5-aad1-20966c9a9f8e
---

When dissolving a Set₁ `data <X>Gen/<X>Term : Obj → Obj → Set₁` (a "term-algebra" / free
category over generators), do NOT reach to BUILD a generic free-category-over-a-quiver or a
hand-rolled `GradedRigCat` instance. The witness tower already HAS the free construction — but
in its **graded-carrier** shape, not a quiver shape: the free object is `LehmerPath n ≅ Perm n`
(`WitnessTower/LehmerPath.agda`), the combine is `_⊕_`, the graded stencil is
`⊕-over : GradedProductOver _+_ 0 LehmerPath` (`OrientationBimonoidal/Properties.agda:48`), and the
universal property is `fold`/`fold-unique` (`OrientationUniversal.agda:53/63`). A term is a
COMBINATION OF GENERATORS up to permutation, which IS `LehmerPath` (≅ Perm). The uniform rewrite:
`<X>Term = LehmerPath`, `[]/++ = start/_⊕_`, `<X>-product = ⊕-over`, `eval = fold`,
`eval-unique = fold-unique`, `<X>-assoc = ⊕-assoc-over`. All Set₀, zero bespoke data.

**Why:** In the ⟡term-algebra-via-witness-tower arc I first searched for a "free CATEGORY over an
arbitrary Set₀ quiver `Gen : Obj→Obj→Set`" — two agents correctly found NO such generic apex exists,
which MISLED me toward building one (a `FreeCat` module, then a 60-line hand-rolled `GradedRigCat`
instance = "a headache", the user said). The tower's free construction is real but has a DIFFERENT
shape: a graded carrier `C : ℕ → Set` + a fold, not a quiver. Searching for the wrong shape made a
present, proven apex look absent — the build-a-bespoke reflex is the same class as the wall-reflex
([[feedback_declaring_a_wall_is_the_rebuild_reflex]]). The `Obj → Obj → Set₁` framing pulls toward
"quiver"; the fix is to translate it to "graded ℕ-carrier" and search THAT.

**How to apply:** Before building any free-construction machinery, translate the target from
`Obj→Obj→Set₁` to the graded question "what is the free `C : ℕ → Set` here, and its fold?" — then
grep the tower for `GradedProductOver` / `LehmerPath` / `fold-unique` / `⊕-over` and instantiate.
The generators' distinct alphabet collapses into the uniform LehmerPath for content-free scaffolding
(no consumer distinguishes the objects); a generator that CARRIES DATA (a Set-valued relation, e.g.
`MarkovGen.lift : … → (X→Y→Set) → …`) is the genuinely-Set₁ hard case that needs the payload in a
Set₀ carrier + the enumerable-objects (ℕ-index) object-drop, NOT the bare LehmerPath collapse.
Verify the recipe with a scratch-probe compile BEFORE touching real files.

Related: [[feedback_route_through_witness_tower]], [[set1-is-grade-collapse]],
[[universal-property-free]], [[feedback_reuse_search_before_feasibility_conclusions]].
