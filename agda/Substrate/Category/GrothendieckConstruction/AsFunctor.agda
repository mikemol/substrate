------------------------------------------------------------------------
-- Substrate.Category.GrothendieckConstruction.AsFunctor
--
-- Substrate-level naming of ∫F as a functor.
--
-- N3 of the N-arc.
--
-- Z3 GrothendieckConstruction takes a Cat-valued functor F : Base →
-- Cat and produces the total category ∫F. The assignment F ↦ ∫F is
-- itself a functor:
--   ∫ : [Base, Cat] → Cat/Base
-- where [Base, Cat] is the functor category and Cat/Base is the
-- slice over Base.
--
-- Per [[grothendieck-coherence-rule]]: the substrate's very mechanism
-- for closing orphan-primitives (Grothendieck construction) is itself
-- a functor whose orphan-status was unaddressed. N3 closes that gap,
-- exposing ∫ at the substrate functor layer.
--
-- Per [[homology-cohomology-recursion]]: this slice IS the recursion
-- — ∫ as a functor is the level-(k+1) cohomology over the level-k
-- ∫-of-individual-functors structure. Each iteration of "fold and
-- reclose Grothendieck" lifts one ∫ from per-instance to functorial.
--
-- Module-parametric per substrate convention.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

open import Level using (Level)

open import Substrate.Category.CategoryOf using (CategoryOf)
open import Substrate.Category.Functor using (Functor)

module Substrate.Category.GrothendieckConstruction.AsFunctor
  {ℓOF ℓMF ℓOC ℓMC : Level}
  -- The functor category [Base, Cat] (= Cat-valued functors over a
  -- fixed Base).
  (FunctorCat : CategoryOf {ℓOF} {ℓMF})
  -- The slice Cat/Base — total categories with projections to Base.
  (CatOverBase : CategoryOf {ℓOC} {ℓMC})
  -- The Grothendieck assignment functor.
  (∫ : Functor FunctorCat CatOverBase)
  where

------------------------------------------------------------------------
-- 1. ∫ as the substrate's named Grothendieck-construction functor.
------------------------------------------------------------------------

Grothendieck-Functor : Functor FunctorCat CatOverBase
Grothendieck-Functor = ∫

------------------------------------------------------------------------
-- 2. Capstone — Grothendieck construction as M1 Functor.
--
-- N3 of the N-arc. With N3 landed, the substrate's CORE coherence-
-- closing mechanism (Z3 ∫F) is itself a substrate functor.
--
-- After N1+N2+N3: the substrate's three load-bearing Z-arc
-- assignments (Aut, CategoryOf, ∫) are all M1 Functor instances.
-- The "fold and reclose Grothendieck" loop has one full iteration
-- visible at the substrate functor layer.
--
-- Per [[grothendieck-coherence-rule]]: each iteration of the
-- recursion exposes the previous iteration's mechanisms as
-- structurally-orphan-free. N1-N3 close the Z-arc's
-- mechanism-orphans.
--
-- Next: N4 PrimeFactoredGauge.AsFunctor.
------------------------------------------------------------------------
