------------------------------------------------------------------------
-- Substrate.Algebra.F2.HodgeDim4.ReservedBridgeAlternatives.Swap.Lookup1
--
-- Swap alternative: lookup at index 1 equals c₂.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.F2.HodgeDim4.ReservedBridgeAlternatives.Swap.Lookup1 where

open import Substrate.Foundation.Fin using (zero; suc)
open import Substrate.Foundation.Vec using ([]; _∷_; lookup)
open import Substrate.Foundation.Eq  using (_≡_; trans; cong)
open import Substrate.Algebra.F2
  using ( F₂; 𝟘; 𝟙; _+_; _·_
        ; +-identityˡ
        ; ·-identityʳ; ·-absorbʳ
        )
open import Substrate.Algebra.F2.HodgeDim4.ReservedBridgeAlternatives.Swap.Forward
  using (vector3-to-selfdual-swap)

lookup-1-swap :
  (c₀ c₁ c₂ : F₂) →
  lookup (vector3-to-selfdual-swap (c₀ ∷ c₁ ∷ c₂ ∷ [])) (suc zero) ≡ c₂
lookup-1-swap c₀ c₁ c₂ =
  trans (cong (_+ ((c₁ · 𝟘) + (c₂ · 𝟙))) (·-absorbʳ c₀))
  (trans (+-identityˡ _)
  (trans (cong (_+ (c₂ · 𝟙)) (·-absorbʳ c₁))
  (trans (+-identityˡ _)
         (·-identityʳ c₂))))
