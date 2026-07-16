------------------------------------------------------------------------
-- Substrate.Category.UniversalProperty.Sheafify
--
-- UP25 of the UP-topos arc per [scratch/up_topos_arc_plan.md].
--
-- Sheafification: a functor sheafify : PSh → Sh left adjoint to the
-- forgetful inclusion. The signature is named; the concrete construction
-- (plus-construction) is deferred to a follow-up arc.
--
-- ⟡ta-upterm: over the Set₀ object-alphabet O (Presheaf/Sheaf now O-form).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Category.UniversalProperty.Sheafify where

open import Substrate.Category.UniversalProperty.Presheaf using (UPPresheaf)
open import Substrate.Category.UniversalProperty.Sheaf using (UPSheaf)

module _ (O : Set) (Hom : O → O → Set) where

  SheafifyType : Set₁
  SheafifyType = UPPresheaf O Hom → UPSheaf O Hom

  -- Concrete construction deferred (the plus-construction).
