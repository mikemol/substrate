------------------------------------------------------------------------
-- Substrate.Algebra.F2.HodgeDim4.ReservedBridgeAlternatives.Swap.Lookup0
--
-- Swap alternative: lookup at index 0 equals c₀.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.F2.HodgeDim4.ReservedBridgeAlternatives.Swap.Lookup0 where

open import Substrate.Foundation.Fin using (zero)
open import Substrate.Foundation.Vec using ([]; _∷_; lookup)
open import Substrate.Foundation.Eq  using (_≡_; trans; cong; cong-trans)
open import Substrate.Algebra.F2
  using ( F₂; 𝟘; _+_; _·_
        ; +-identityˡ; +-identityʳ
        ; ·-identityʳ; ·-absorbʳ
        )
open import Substrate.Algebra.F2.HodgeDim4.ReservedBridgeAlternatives.Swap.Forward
  using (vector3-to-selfdual-swap)

lookup-0-swap :
  (c₀ c₁ c₂ : F₂) →
  lookup (vector3-to-selfdual-swap (c₀ ∷ c₁ ∷ c₂ ∷ [])) zero ≡ c₀
lookup-0-swap c₀ c₁ c₂ =
  cong-trans (_+ ((c₁ · 𝟘) + (c₂ · 𝟘))) (·-identityʳ c₀)
  (cong-trans (c₀ +_) (cong (_+ (c₂ · 𝟘)) (·-absorbʳ c₁))
  (cong-trans (c₀ +_) (+-identityˡ _)
  (cong-trans (c₀ +_) (·-absorbʳ c₂)
         (+-identityʳ c₀))))
