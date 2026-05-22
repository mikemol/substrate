------------------------------------------------------------------------
-- Substrate.Algebra.F2.HodgeDim4.ReservedBridgeAlternatives.Cyclic.RoundTrip
--
-- selfdual-coefficients-cyclic ∘ vector3-to-selfdual-cyclic ≡ id.
-- Closes by chaining the three Lookup-{0,1,2}-cyclic lemmas.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.F2.HodgeDim4.ReservedBridgeAlternatives.Cyclic.RoundTrip where

open import Substrate.Foundation.Fin using (zero; suc)
open import Substrate.Foundation.Vec using ([]; _∷_; lookup)
open import Substrate.Foundation.Eq  using (_≡_; trans; cong)
open import Substrate.Algebra.F2.Vector using (Vector)
open import Substrate.Algebra.F2.HodgeDim4.ReservedBridgeAlternatives.Cyclic.Forward
  using (vector3-to-selfdual-cyclic)
open import Substrate.Algebra.F2.HodgeDim4.ReservedBridgeAlternatives.Cyclic.Inverse
  using (selfdual-coefficients-cyclic)
open import Substrate.Algebra.F2.HodgeDim4.ReservedBridgeAlternatives.Cyclic.Lookup1
  using (lookup-1-cyclic)
open import Substrate.Algebra.F2.HodgeDim4.ReservedBridgeAlternatives.Cyclic.Lookup2
  using (lookup-2-cyclic)
open import Substrate.Algebra.F2.HodgeDim4.ReservedBridgeAlternatives.Cyclic.Lookup0
  using (lookup-0-cyclic)

selfdual-coefficients-cyclic-roundtrip :
  (v : Vector 3) →
  selfdual-coefficients-cyclic (vector3-to-selfdual-cyclic v) ≡ v
selfdual-coefficients-cyclic-roundtrip (c₀ ∷ c₁ ∷ c₂ ∷ []) =
  trans (cong (λ x →
                x ∷
                lookup (vector3-to-selfdual-cyclic (c₀ ∷ c₁ ∷ c₂ ∷ [])) (suc (suc zero)) ∷
                lookup (vector3-to-selfdual-cyclic (c₀ ∷ c₁ ∷ c₂ ∷ [])) zero ∷ [])
              (lookup-1-cyclic c₀ c₁ c₂))
  (trans (cong (λ x →
                 c₀ ∷ x ∷
                 lookup (vector3-to-selfdual-cyclic (c₀ ∷ c₁ ∷ c₂ ∷ [])) zero ∷ [])
               (lookup-2-cyclic c₀ c₁ c₂))
         (cong (λ x → c₀ ∷ c₁ ∷ x ∷ [])
               (lookup-0-cyclic c₀ c₁ c₂)))
