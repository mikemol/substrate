------------------------------------------------------------------------
-- Substrate.Category.PrimeFactoredGauge.ActedUponByAut
--
-- O3 of the O-arc. The natural transformation witnessing that every
-- PFG instance carries an Aut-action via its gauge group.
--
-- Per [[grothendieck-coherence-rule]]: N4 PFG-functor + N1 Aut-functor
-- compose; the action "PFG instance ↦ Aut acting on it" is itself a
-- natural transformation between the two functors (after suitable
-- composition with forgetful maps).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

open import Substrate.Foundation.Level using (Level)

open import Substrate.Category.CategoryOf using (CategoryOf)
open import Substrate.Category.Functor using (Functor)
open import Substrate.Category.NaturalTransformation
  using (NaturalTransformation)

module Substrate.Category.PrimeFactoredGauge.ActedUponByAut
  {ℓOG ℓMG ℓOP ℓMP : Level}
  (GroupCat : CategoryOf {ℓOG} {ℓMG})
  (PFGCat : CategoryOf {ℓOP} {ℓMP})
  (PFG-Functor : Functor GroupCat PFGCat)
  (Aut-Functor : Functor GroupCat PFGCat)
  (Aut-action : NaturalTransformation PFG-Functor Aut-Functor)
  where

PFG-Aut-Action : NaturalTransformation PFG-Functor Aut-Functor
PFG-Aut-Action = Aut-action

------------------------------------------------------------------------
-- Substrate-named nat-trans for the gauge-action of Aut on PFG.
------------------------------------------------------------------------
