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

open import Substrate.Foundation.Product using (Σ)
open import Substrate.Category.UniversalProperty.Presheaf using (UPPresheaf)
open import Substrate.Category.UniversalProperty.Sheaf using (UPSheaf)

module _ (O : Set) (Hom : O → O → Set) where

  -- ⟡rc-topos (⟡set1-rerank2): UPPresheaf's `F` and UPSheaf's `F`/
  -- `descent-stated` are now PARAMETERS — sheafify's codomain genuinely
  -- quantifies over the resulting fiber family + descent obligation, so
  -- this stays a documented Set₁ Σ-holder (same shape as the other
  -- signature-only defs in this file/family).
  SheafifyType : Set₁
  SheafifyType = (F : O → Set) → UPPresheaf O Hom F →
                 Σ (O → Set) (λ G → Σ Set (λ d → UPSheaf O Hom G d))

  -- Concrete construction deferred (the plus-construction).
