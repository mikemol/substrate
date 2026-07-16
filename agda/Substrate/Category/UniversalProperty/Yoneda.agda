------------------------------------------------------------------------
-- Substrate.Category.UniversalProperty.Yoneda
--
-- UP22 of the UP-topos arc per [scratch/up_topos_arc_plan.md].
--
-- The Yoneda embedding よ : UPCategory → PSh(UPCategory), over the Set₀
-- object alphabet O with homs UPTermO O Hom (⟡ta-upterm):
--
--   よ(U) (V) = UPTermO O Hom V U   (the set of morphisms V → U)
--   よ(U) (t : W → V) (s : UPTermO O Hom V U) = s ∘ t = t ++ᵤO s
--
-- Functoriality at the term level:
--   action []O s = s  (definitionally via []O ++ᵤO s = s)
--   action (u ++ᵤO t) s = action u (action t s) (associativity)
--
-- ⟡ta-upterm: よ now lands at the PLAIN `UPPresheaf O Hom` (F/action/
-- pres-id/pres-∘). The old Set₂ `UPPresheaf₁` wrapper is DELETED — the
-- Set₀ term-forms make it unnecessary.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Category.UniversalProperty.Yoneda where

open import Substrate.Foundation.Eq
  using (_≡_; refl)

open import Substrate.Category.UniversalProperty.Term
  using (UPTermO; _++ᵤO_)
open import Substrate.Category.UniversalProperty.Category
  using (++ᵤO-assoc)
open import Substrate.Category.UniversalProperty.Presheaf
  using (UPPresheaf)

module _ (O : Set) (Hom : O → O → Set) where

  ------------------------------------------------------------------------
  -- The Yoneda embedding よ : O → UPPresheaf O Hom.
  --
  --   F V         = UPTermO O Hom V U   (morphisms V → U)
  --   action t s  = t ++ᵤO s            (precomposition = s ∘ t)
  --   pres-id     = refl                ([]O ++ᵤO s = s definitionally)
  --   pres-∘      = ++ᵤO-assoc          (append associativity)
  ------------------------------------------------------------------------

  よ : O → UPPresheaf O Hom
  よ U = record
    { F       = λ V → UPTermO O Hom V U
    ; action  = λ t s → t ++ᵤO s
    ; pres-id = λ s → refl
    ; pres-∘  = λ t u x → ++ᵤO-assoc u t x
    }

------------------------------------------------------------------------
-- Capstone for UP22.
--
-- The Yoneda embedding lands at the plain Set₁ `UPPresheaf O Hom`.
-- UP23 specialises to sheaves; UP24-UP30 close Phase 3.
------------------------------------------------------------------------
