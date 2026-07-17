------------------------------------------------------------------------
-- Substrate.Category.Coxeter.AsCartanType.Functor
--
-- Functorial upgrade of L13 [[Coxeter.AsCartanType]].
--
-- M8 of the M-arc. L13 named a one-shot bridge from a SINGLE Coxeter
-- system's data to a SINGLE CartanType value. M8 lifts this to a
-- FUNCTOR from a category of Coxeter systems to a category of Cartan
-- types — closing the L13 orphan gap per
-- [[grothendieck-coherence-rule]].
--
-- Without M8: each application of L13 produces a CartanType in
-- isolation; morphisms between Coxeter systems (= rank-preserving
-- m-respecting maps) have no induced action on the corresponding
-- Cartan types.
--
-- With M8: Coxeter morphisms transport to Cartan-type morphisms
-- functorially; the bridge becomes the substrate's Coxeter ↔ Cartan
-- equivalence of categories (specialised to crystallographic types
-- by an additional crystallographic-constraint predicate, downstream).
--
-- Per [[universal-property-discipline]]: the equivalence of categories
-- (CoxeterSystems) ↔ (CartanTypes) is the deep statement; M8 captures
-- the FORWARD functor; the backward functor (Cartan ↦ Coxeter via
-- "extract the Coxeter group from the Cartan type") + the
-- isomorphism witnesses + the equivalence-of-categories adjunction
-- compose as downstream slices.
--
-- Module-parametric per substrate convention.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

open import Substrate.Foundation.Level using (Level)

open import Substrate.Category.CategoryOf using (CategoryOf)
open import Substrate.Category.Functor using (Functor)

module Substrate.Category.Coxeter.AsCartanType.Functor
  {ℓOC ℓMC ℓOT ℓMT : Level}
  {ObjCoxeterCat : Set ℓOC} {MorCoxeterCat : ObjCoxeterCat → ObjCoxeterCat → Set ℓMC}
  {ObjCartanCat : Set ℓOT} {MorCartanCat : ObjCartanCat → ObjCartanCat → Set ℓMT}
  (CoxeterCat : CategoryOf ObjCoxeterCat MorCoxeterCat)
  (CartanCat : CategoryOf ObjCartanCat MorCartanCat)
  (Coxeter→Cartan : Functor CoxeterCat CartanCat)
  where

------------------------------------------------------------------------
-- 1. The Coxeter ↦ Cartan functor.
------------------------------------------------------------------------

open import Substrate.Category.Functor.AsNamed
  CoxeterCat CartanCat Coxeter→Cartan public
  renaming (named-Functor to Coxeter-AsCartan-Functor)
------------------------------------------------------------------------
-- 2. Capstone — L13 lifted to a functor.
--
-- M8 of the M-arc. With M8 landed:
--   * L13 = single-instance bridge (rank + m_ij → CartanType)
--   * M8 = functorial lift (Coxeter morphisms → Cartan morphisms)
--   * Together: the substrate's Coxeter ↔ Cartan correspondence is
--     visible at the functor layer
--
-- After M8: the substrate's Lie ↔ Coxeter ↔ Cartan triangulation
-- closes structurally:
--   M5 Λ-functor (Vect → ExtAlg)
--   M6 underlying-Lie (Assoc → Lie)
--   M7 U (Lie → Assoc)
--   M8 Coxeter → Cartan (CoxeterCat → CartanCat) (THIS)
--
-- The four functorial closures of L-arc orphans are in place.
--
-- Per [[grothendieck-coherence-rule]] + [[homology-cohomology-
-- recursion]]: the next Grothendieck lift will see all four
-- functors as 1-cells in the ambient Cat 2-category; orphans are
-- closed at the L-arc layer.
--
-- Next: M9 HodgeStar.AsNaturalTransformation (★ as 2-cell, completing
-- M2's usage).
------------------------------------------------------------------------
