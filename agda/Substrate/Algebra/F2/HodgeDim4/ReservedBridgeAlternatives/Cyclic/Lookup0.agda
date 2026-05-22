------------------------------------------------------------------------
-- Substrate.Algebra.F2.HodgeDim4.ReservedBridgeAlternatives.Cyclic.Lookup0
--
-- Cyclic alternative: lookup at index 0 of the encoded bivector
-- equals the trailing coefficient c₂.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.F2.HodgeDim4.ReservedBridgeAlternatives.Cyclic.Lookup0 where

open import Substrate.Foundation.Fin using (zero; suc)
open import Substrate.Foundation.Vec using ([]; _∷_; lookup)
open import Substrate.Foundation.Eq  using (_≡_; trans; cong)
open import Substrate.Algebra.F2
  using ( F₂; 𝟘; 𝟙; _+_; _·_
        ; +-identityˡ
        ; ·-identityʳ; ·-absorbʳ
        )
open import Substrate.Algebra.F2.HodgeDim4.ReservedBridgeAlternatives.Cyclic.Forward
  using (vector3-to-selfdual-cyclic)

lookup-0-cyclic :
  (c₀ c₁ c₂ : F₂) →
  lookup (vector3-to-selfdual-cyclic (c₀ ∷ c₁ ∷ c₂ ∷ [])) zero ≡ c₂
lookup-0-cyclic c₀ c₁ c₂ =
  trans (cong (_+ ((c₁ · 𝟘) + (c₂ · 𝟙))) (·-absorbʳ c₀))
  (trans (+-identityˡ _)
  (trans (cong (_+ (c₂ · 𝟙)) (·-absorbʳ c₁))
  (trans (+-identityˡ _)
         (·-identityʳ c₂))))
