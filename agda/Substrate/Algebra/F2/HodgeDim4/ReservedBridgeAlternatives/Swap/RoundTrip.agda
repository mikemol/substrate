------------------------------------------------------------------------
-- Substrate.Algebra.F2.HodgeDim4.ReservedBridgeAlternatives.Swap.RoundTrip
--
-- selfdual-coefficients-swap ∘ vector3-to-selfdual-swap ≡ id.
-- Closes by chaining the three Lookup-{0,1,2}-swap lemmas.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.F2.HodgeDim4.ReservedBridgeAlternatives.Swap.RoundTrip where

open import Substrate.Foundation.Fin using (zero; suc)
open import Substrate.Foundation.Vec using ([]; _∷_; lookup)
open import Substrate.Foundation.Eq  using (_≡_; trans; cong)
open import Substrate.Algebra.F2.Vector using (Vector)
open import Substrate.Algebra.F2.HodgeDim4.ReservedBridgeAlternatives.Swap.Forward
  using (vector3-to-selfdual-swap)
open import Substrate.Algebra.F2.HodgeDim4.ReservedBridgeAlternatives.Swap.Inverse
  using (selfdual-coefficients-swap)
open import Substrate.Algebra.F2.HodgeDim4.ReservedBridgeAlternatives.Swap.Lookup0
  using (lookup-0-swap)
open import Substrate.Algebra.F2.HodgeDim4.ReservedBridgeAlternatives.Swap.Lookup2
  using (lookup-2-swap)
open import Substrate.Algebra.F2.HodgeDim4.ReservedBridgeAlternatives.Swap.Lookup1
  using (lookup-1-swap)

selfdual-coefficients-swap-roundtrip :
  (v : Vector 3) →
  selfdual-coefficients-swap (vector3-to-selfdual-swap v) ≡ v
selfdual-coefficients-swap-roundtrip (c₀ ∷ c₁ ∷ c₂ ∷ []) =
  trans (cong (λ x →
                x ∷
                lookup (vector3-to-selfdual-swap (c₀ ∷ c₁ ∷ c₂ ∷ [])) (suc (suc zero)) ∷
                lookup (vector3-to-selfdual-swap (c₀ ∷ c₁ ∷ c₂ ∷ [])) (suc zero) ∷ [])
              (lookup-0-swap c₀ c₁ c₂))
  (trans (cong (λ x →
                 c₀ ∷ x ∷
                 lookup (vector3-to-selfdual-swap (c₀ ∷ c₁ ∷ c₂ ∷ [])) (suc zero) ∷ [])
               (lookup-2-swap c₀ c₁ c₂))
         (cong (λ x → c₀ ∷ c₁ ∷ x ∷ [])
               (lookup-1-swap c₀ c₁ c₂)))
