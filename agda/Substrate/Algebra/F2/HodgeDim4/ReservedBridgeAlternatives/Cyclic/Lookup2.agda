------------------------------------------------------------------------
-- Substrate.Algebra.F2.HodgeDim4.ReservedBridgeAlternatives.Cyclic.Lookup2
--
-- Cyclic alternative: lookup at index 2 of the encoded bivector
-- equals the second coefficient c₁.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.F2.HodgeDim4.ReservedBridgeAlternatives.Cyclic.Lookup2 where

open import Substrate.Foundation.Fin using (zero; suc)
open import Substrate.Foundation.Vec using ([]; _∷_; lookup)
open import Substrate.Foundation.Eq  using (_≡_; trans; cong)
open import Substrate.Algebra.F2
  using ( F₂; 𝟘; 𝟙; _+_; _·_
        ; +-identityˡ; +-identityʳ
        ; ·-identityʳ; ·-absorbʳ
        )
open import Substrate.Algebra.F2.HodgeDim4.ReservedBridgeAlternatives.Cyclic.Forward
  using (vector3-to-selfdual-cyclic)

lookup-2-cyclic :
  (c₀ c₁ c₂ : F₂) →
  lookup (vector3-to-selfdual-cyclic (c₀ ∷ c₁ ∷ c₂ ∷ [])) (suc (suc zero)) ≡ c₁
lookup-2-cyclic c₀ c₁ c₂ =
  trans (cong (_+ ((c₁ · 𝟙) + (c₂ · 𝟘))) (·-absorbʳ c₀))
  (trans (+-identityˡ _)
  (trans (cong (_+ (c₂ · 𝟘)) (·-identityʳ c₁))
  (trans (cong (c₁ +_) (·-absorbʳ c₂))
         (+-identityʳ c₁))))
