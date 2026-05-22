------------------------------------------------------------------------
-- Substrate.Category.Modification
--
-- Q2 of the Q-arc. 3-cells (modifications between nat-trans).
--
-- Per [[grothendieck-coherence-rule]]: with 0/1/2-cells in place,
-- 3-cells provide the next layer of coherence. Module-parametric;
-- consumers supply the modification data.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Category.Modification where

open import Substrate.Foundation.Level using (Level; _⊔_) renaming (suc to lsuc)

open import Substrate.Category.CategoryOf using (CategoryOf)
open import Substrate.Category.Functor using (Functor)
open import Substrate.Category.NaturalTransformation
  using (NaturalTransformation)

private
  variable
    ℓOC ℓMC ℓOD ℓMD : Level

------------------------------------------------------------------------
-- Modification — parametric record bundling the modification's
-- component family + coherence (= the modification square commutes).
-- User supplies the component-type and coherence per concrete site.
------------------------------------------------------------------------

record Modification
  {C : CategoryOf {ℓOC} {ℓMC}}
  {D : CategoryOf {ℓOD} {ℓMD}}
  {F G : Functor C D}
  (α β : NaturalTransformation F G)
  (Component : Set ℓMD) : Set (ℓOC ⊔ ℓMD) where
  field
    components : CategoryOf.Obj C → Component
