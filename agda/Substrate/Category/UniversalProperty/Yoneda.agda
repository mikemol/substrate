------------------------------------------------------------------------
-- Substrate.Category.UniversalProperty.Yoneda
--
-- UP22 of the UP-topos arc per [scratch/up_topos_arc_plan.md].
--
-- The Yoneda embedding よ : UPCategory → PSh(UPCategory):
--
--   よ(U) (V) = UPTerm V U   (the set of morphisms V → U)
--   よ(U) (t : W → V) (s : UPTerm V U) = s ∘ t = t ++ᵤ s
--
-- Functoriality at the term level:
--   action [] s = s  (definitionally via [] ++ᵤ s = s)
--   action (u ++ᵤ t) s = action u (action t s) (associativity)
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Category.UniversalProperty.Yoneda where

open import Substrate.Foundation.Eq
  using (_≡_; refl; sym; trans; cong)

open import Substrate.Category.UniversalProperty using (UPArrow)
open import Substrate.Category.UniversalProperty.Term
  using (UPTerm; []; _++ᵤ_)
open import Substrate.Category.UniversalProperty.Category
  using (++ᵤ-identityˡ; ++ᵤ-assoc)
open import Substrate.Category.UniversalProperty.Presheaf
  using (UPPresheaf)

------------------------------------------------------------------------
-- 1. UPTerm has SET-level fields and we need Set; the UPTerm
--    indexes its objects into Set₁. We package it via a wrapping
--    Set₁-valued presheaf instead — UP22's よ produces a
--    Set₁-valued presheaf.
--
-- Substrate-honest: define a level-bumped variant `UPPresheaf₁`
-- and exhibit よ as an instance.
------------------------------------------------------------------------

record UPPresheaf₁ : Set₃ where
  field
    F₁        : UPArrow → Set₁
    action₁   : {U V : UPArrow} →
                UPTerm V U → F₁ U → F₁ V
    pres-id₁  : {U : UPArrow} (x : F₁ U) → action₁ {U} {U} [] x ≡ x
    pres-∘₁   : {U V W : UPArrow}
                (t : UPTerm V U) (u : UPTerm W V) (x : F₁ U) →
                action₁ (u ++ᵤ t) x ≡ action₁ u (action₁ t x)

open UPPresheaf₁ public

------------------------------------------------------------------------
-- 2. The Yoneda embedding よ : UPArrow → UPPresheaf₁.
------------------------------------------------------------------------

よ : UPArrow → UPPresheaf₁
よ U = record
  { F₁       = λ V → UPTerm V U
  ; action₁  = λ t s → t ++ᵤ s
  ; pres-id₁ = λ s → refl
  ; pres-∘₁  = λ t u x → ++ᵤ-assoc u t x
  }

------------------------------------------------------------------------
-- 3. Capstone for UP22.
--
-- The Yoneda embedding lands at Set₁-level (because UPTerm is
-- Set₁-valued). UP23 specialises to sheaves; UP24-UP30 close
-- Phase 3.
------------------------------------------------------------------------
