------------------------------------------------------------------------
-- Substrate.Category.UniversalProperty.ConstantSheaf
--
-- UP26 of the UP-topos arc per [scratch/up_topos_arc_plan.md].
--
-- The constant presheaf at any Set A: F(U) = A for every U,
-- action(t) = id. It IS a presheaf trivially. Its sheafification
-- gives the "constant sheaf at A."
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Category.UniversalProperty.ConstantSheaf where

open import Substrate.Foundation.Eq using (_≡_; refl)
open import Substrate.Category.UniversalProperty using (UPArrowP)
open import Substrate.Category.UniversalProperty.Term using (UPTerm)
open import Substrate.Category.UniversalProperty.Presheaf using (UPPresheaf)

------------------------------------------------------------------------
-- 1. The constant presheaf at A.
------------------------------------------------------------------------

constant-Presheaf : Set → UPPresheaf
constant-Presheaf A = record
  { F       = λ _ → A
  ; action  = λ _ x → x
  ; pres-id = λ _ → refl
  ; pres-∘  = λ _ _ _ → refl
  }

------------------------------------------------------------------------
-- 2. Capstone for UP26.
--
-- Constant-Presheaf lands. UP27 supplies pullback of sheaves.
------------------------------------------------------------------------
