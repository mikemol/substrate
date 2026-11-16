------------------------------------------------------------------------
-- Substrate.Algebra.F2.HodgeDim4.ReservedBridgeAlternatives.Swap.Lookup1
--
-- Swap alternative: lookup at index 1 equals c₂.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.F2.HodgeDim4.ReservedBridgeAlternatives.Swap.Lookup1 where

open import Substrate.Foundation.Fin.Literals using (₀; ₁; ₂)
open import Substrate.Foundation.Vec using ([]; _∷_; lookup)
open import Substrate.Algebra.F2.AbsorbR
open import Substrate.Algebra.F2.F2
open import Substrate.Algebra.F2.IdentityR
open import Substrate.Algebra.F2.Op
open import Substrate.Algebra.F2.PlusF
open import Substrate.Algebra.F2.PlusIdentityL
open import Substrate.Algebra.F2.HodgeDim4.ReservedBridgeAlternatives.Swap.Forward
  using (vector3-to-selfdual-swap)
open import Substrate.Foundation.Eq
open import Substrate.Foundation.Eq.Trans
open import Substrate.Foundation.Eq.CongTrans

lookup-1-swap :
  (c₀ c₁ c₂ : F₂) →
  lookup (vector3-to-selfdual-swap (c₀ ∷ c₁ ∷ c₂ ∷ [])) ₁ ≡ c₂
lookup-1-swap c₀ c₁ c₂ =
  cong-trans (_+F ((c₁ · 𝟘) +F (c₂ · 𝟙))) (·-absorbʳ c₀)
  (trans (+-identityˡ _)
  (cong-trans (_+F (c₂ · 𝟙)) (·-absorbʳ c₁)
  (trans (+-identityˡ _)
         (·-identityʳ c₂))))
