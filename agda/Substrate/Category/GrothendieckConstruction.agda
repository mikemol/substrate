------------------------------------------------------------------------
-- Substrate.Category.GrothendieckConstruction
--
-- The Grothendieck construction primitive: given a base category C
-- and a (pseudo-)functor F : C → Cat, the total category ∫F has
-- objects (c, x) with c ∈ C, x ∈ F(c), and morphisms threading both
-- base and fiber structure.
--
-- Z3 of the 10-slice Grothendieck-closure arc per
-- [[prime-factored-gauge-arc]] follow-on (per the user's "where does
-- the system lack closure" audit).
--
-- KEY STRUCTURAL CONTENT:
--
--   For any base set C + a fiber function F : C → Set, the
--   Grothendieck construction packages "every (c, x) with x ∈ F(c)"
--   as a single substrate object. With added morphism structure,
--   this becomes the full ∫F total category.
--
--   The substrate's higher-layer primitives (Cone, GTorsor, PFG,
--   etc.) all have implicit Grothendieck-style structure: for each
--   "base context" (e.g., a group G), there's a "fiber category"
--   (e.g., G-torsors, PFGs-over-G). This primitive makes that
--   structure substrate-internal.
--
-- Per [[universal-property-discipline]] + [[categorical-name-first]]:
-- "Grothendieck construction" is the standard categorical name for
-- the fibered-category unpacking; ∫F captures its universal property
-- as "the category whose objects are pairs."
--
-- Substrate-pragmatic scope: this primitive provides the SHAPE
-- (base + fiber + projection + total morphism placeholder) without
-- forcing the full strict-/pseudo-functor category-theoretic
-- formalism. Per [[anneal-don't-leap]]: detailed 2-categorical
-- machinery deferred; the structural type-target is in place.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Category.GrothendieckConstruction where

open import Level using (Level; _⊔_) renaming (suc to lsuc)
open import Substrate.Foundation.Product using (Σ; _,_; proj₁; proj₂)

private
  variable
    ℓC ℓF ℓM : Level

------------------------------------------------------------------------
-- 1. The base/fiber decomposition.
--
-- Records the basic data of a Grothendieck-style fibration:
--   * Base : Set ℓC — the base set / category of objects
--   * Fiber : Base → Set ℓF — fiber over each base point
--
-- The total object set is Σ Base Fiber (= the disjoint union of
-- fibers). Morphisms in ∫F are supplied as a separate record below.
------------------------------------------------------------------------

record Fibration (Base : Set ℓC) (Fiber : Base → Set ℓF) : Set (ℓC ⊔ ℓF) where
  Total : Set (ℓC ⊔ ℓF)
  Total = Σ Base Fiber

  -- Projection to base.
  proj-base : Total → Base
  proj-base = proj₁

  -- Projection to fiber (over the base point).
  proj-fiber : (t : Total) → Fiber (proj-base t)
  proj-fiber = proj₂

------------------------------------------------------------------------
-- 2. The GrothendieckConstruction record.
--
-- Bundles a Fibration with morphism data (base-morphisms + fiber-
-- morphisms + their composition into total-morphisms).
--
-- Morphisms in ∫F (covariant version):
--   (c, x) → (c', x') is a pair (f : c → c', φ : F(f)(x) → x')
--   where F(f) : F(c) → F(c') is the fiber's transport.
--
-- Substrate-pragmatic encoding: parametric over base + fiber
-- morphism types; the user supplies them per-instance.
------------------------------------------------------------------------

record GrothendieckConstruction
  (Base : Set ℓC)
  (Fiber : Base → Set ℓF)
  (BaseMorph : Base → Base → Set ℓM)
  -- Fiber-transport: for each f : c → c', a map F(c) → F(c').
  (FiberTransport :
    (c c' : Base) → BaseMorph c c' → Fiber c → Fiber c') :
  Set (ℓC ⊔ ℓF ⊔ ℓM) where

  -- The total set ∫F.
  Total : Set (ℓC ⊔ ℓF)
  Total = Σ Base Fiber

  -- The morphisms in ∫F at the base-morphism level (= just the f
  -- part, before threading any fiber-morphism). Full ∫F-morphisms
  -- (= pairs (f, φ)) require a fiber-morphism layer which the user
  -- supplies per-instance via the Fiber's own Substrate.Category.
  -- Morphism record.
  TotalMorph-base : Total → Total → Set ℓM
  TotalMorph-base (c , _) (c' , _) = BaseMorph c c'

------------------------------------------------------------------------
-- 3. Capstone — Grothendieck construction primitive in place.
--
-- Z3 of the 10-slice Z-arc. With Z3 landed, the substrate has the
-- Grothendieck-construction shape as a substrate primitive. Concrete
-- instances (the fibrations of substrate's higher primitives) can
-- now name themselves as Grothendieck constructions.
--
-- Substrate-pragmatic scope: the morphism layer is supplied
-- parametrically. Full strict / pseudo-functor formalism (2-cat
-- variants) is downstream specialization work.
--
-- Concrete fibration instances expected:
--   * GTorsor over Group: Base = groups, Fiber = G-torsor sets.
--   * PrimeFactoredGauge over PrimeFactoredGroup: Base = groups with
--     Sylow data, Fiber = PFG instances over them.
--   * ConjugationCoalgebra over Group: Base = groups, Fiber = class
--     structures.
--   * GriessAlgebra over CommutativeNonAssociativeAlgebra: Base =
--     CNAA instances, Fiber = the specific 196,884-dim algebras.
--   * etc.
--
-- Each concrete fibration discharges the Grothendieck-closure gap
-- at its layer.
--
-- Per [[shadow-architecture]]: Z3 is a foundational primitive (DBE)
-- — the structural target without forcing specific implementations.
------------------------------------------------------------------------
