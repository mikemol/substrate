------------------------------------------------------------------------
-- Substrate.Category.UniversalProperty.Sheafify
--
-- UP25 of the UP-topos arc per [scratch/up_topos_arc_plan.md].
--
-- Sheafification: a functor sheafify : PSh(UPCategory) → Sh(UPSite)
-- left adjoint to the forgetful inclusion. The signature is named;
-- concrete construction (the plus-construction, double-plus, etc.)
-- is deferred to a follow-up arc.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Category.UniversalProperty.Sheafify where

open import Substrate.Category.UniversalProperty.Presheaf using (UPPresheaf)
open import Substrate.Category.UniversalProperty.Sheaf using (UPSheaf)

------------------------------------------------------------------------
-- 1. Sheafification signature.
------------------------------------------------------------------------

SheafifyType : Set₁
SheafifyType = UPPresheaf → UPSheaf

-- Concrete construction deferred. The standard "plus-construction"
-- discharges this via two iterations of pointwise sieve-quotients.

------------------------------------------------------------------------
-- 2. Capstone for UP25.
--
-- Sheafification signature lands. UP26-UP30 close Phase 3.
------------------------------------------------------------------------
