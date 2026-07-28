------------------------------------------------------------------------
-- Substrate.Algebra.F2.HodgeDim4.ReservedBridgeAlternatives.Cyclic.Lookup1
--
-- Cyclic alternative: lookup at index 1 of the encoded bivector
-- equals the leading coefficient c₀.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.F2.HodgeDim4.ReservedBridgeAlternatives.Cyclic.Lookup1 where

open import Substrate.Foundation.Fin.Literals using (₀; ₁; ₂)
open import Substrate.Foundation.Vec using ([]; _∷_; lookup)
open import Substrate.Foundation.Eq  using (_≡_; trans; cong; cong-trans)
open import Substrate.Algebra.F2
  using ( F₂; 𝟘; 𝟙; _+_; _·_
        ; +-identityˡ; +-identityʳ
        ; ·-identityʳ; ·-absorbʳ
        )
open import Substrate.Algebra.F2.HodgeDim4.ReservedBridgeAlternatives.Cyclic.Forward
  using (vector3-to-selfdual-cyclic)

lookup-1-cyclic :
  (c₀ c₁ c₂ : F₂) →
  lookup (vector3-to-selfdual-cyclic (c₀ ∷ c₁ ∷ c₂ ∷ [])) ₁ ≡ c₀
lookup-1-cyclic c₀ c₁ c₂ =
  cong-trans (_+ ((c₁ · 𝟘) + (c₂ · 𝟘))) (·-identityʳ c₀)
  (cong-trans (c₀ +_) (cong (_+ (c₂ · 𝟘)) (·-absorbʳ c₁))
  (cong-trans (c₀ +_) (+-identityˡ _)
  (cong-trans (c₀ +_) (·-absorbʳ c₂)
         (+-identityʳ c₀))))
