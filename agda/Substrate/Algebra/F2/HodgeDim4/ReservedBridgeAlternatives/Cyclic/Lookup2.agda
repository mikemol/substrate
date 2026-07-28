------------------------------------------------------------------------
-- Substrate.Algebra.F2.HodgeDim4.ReservedBridgeAlternatives.Cyclic.Lookup2
--
-- Cyclic alternative: lookup at index 2 of the encoded bivector
-- equals the second coefficient c₁.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.F2.HodgeDim4.ReservedBridgeAlternatives.Cyclic.Lookup2 where

open import Substrate.Foundation.Fin.Literals using (₀; ₁; ₂)
open import Substrate.Foundation.Vec using ([]; _∷_; lookup)
open import Substrate.Foundation.Eq  using (_≡_; trans; cong-trans)
open import Substrate.Algebra.F2
  using ( F₂; 𝟘; 𝟙; _+_; _·_
        ; +-identityˡ; +-identityʳ
        ; ·-identityʳ; ·-absorbʳ
        )
open import Substrate.Algebra.F2.HodgeDim4.ReservedBridgeAlternatives.Cyclic.Forward
  using (vector3-to-selfdual-cyclic)

lookup-2-cyclic :
  (c₀ c₁ c₂ : F₂) →
  lookup (vector3-to-selfdual-cyclic (c₀ ∷ c₁ ∷ c₂ ∷ [])) ₂ ≡ c₁
lookup-2-cyclic c₀ c₁ c₂ =
  cong-trans (_+ ((c₁ · 𝟙) + (c₂ · 𝟘))) (·-absorbʳ c₀)
  (trans (+-identityˡ _)
  (cong-trans (_+ (c₂ · 𝟘)) (·-identityʳ c₁)
  (cong-trans (c₁ +_) (·-absorbʳ c₂)
         (+-identityʳ c₁))))
