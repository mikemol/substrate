------------------------------------------------------------------------
-- Substrate.Algebra.F2.HodgeDim4.ReservedBridgeAlternatives.Swap.Lookup0
--
-- Swap alternative: lookup at index 0 equals c₀.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.F2.HodgeDim4.ReservedBridgeAlternatives.Swap.Lookup0 where

open import Substrate.Foundation.Fin.Fin
open import Substrate.Foundation.Vec using ([]; _∷_; lookup)
open import Substrate.Algebra.F2.AbsorbR
open import Substrate.Algebra.F2.F2
open import Substrate.Algebra.F2.IdentityR
open import Substrate.Algebra.F2.Op
open import Substrate.Algebra.F2.PlusF
open import Substrate.Algebra.F2.PlusIdentityL
open import Substrate.Algebra.F2.PlusIdentityR
open import Substrate.Algebra.F2.HodgeDim4.ReservedBridgeAlternatives.Swap.Forward
  using (vector3-to-selfdual-swap)
open import Substrate.Foundation.Eq
open import Substrate.Foundation.Eq.Trans
open import Substrate.Foundation.Eq.Cong
open import Substrate.Foundation.Eq.CongTrans

lookup-0-swap :
  (c₀ c₁ c₂ : F₂) →
  lookup (vector3-to-selfdual-swap (c₀ ∷ c₁ ∷ c₂ ∷ [])) zero ≡ c₀
lookup-0-swap c₀ c₁ c₂ =
  cong-trans (_+F ((c₁ · 𝟘) +F (c₂ · 𝟘))) (·-identityʳ c₀)
  (cong-trans (c₀ +F_) (cong (_+F (c₂ · 𝟘)) (·-absorbʳ c₁))
  (cong-trans (c₀ +F_) (+-identityˡ _)
  (cong-trans (c₀ +F_) (·-absorbʳ c₂)
         (+-identityʳ c₀))))
