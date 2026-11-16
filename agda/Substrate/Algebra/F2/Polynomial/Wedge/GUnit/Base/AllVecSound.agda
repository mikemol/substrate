------------------------------------------------------------------------
-- Substrate.Algebra.F2.Polynomial.Wedge.GUnit.Base.AllVecSound
--
-- Defines: all-vec-sound
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.Algebra.F2.Polynomial.Wedge.GUnit.Base; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.F2.Polynomial.Wedge.GUnit.Base.AllVecSound where

open import Substrate.Foundation.Nat.Nat
open import Substrate.Foundation.Vec
open import Substrate.Foundation.Bool.And
open import Substrate.Foundation.Bool.Bool
open import Substrate.Foundation.Bool.Properties.AndElimL
open import Substrate.Foundation.Bool.Properties.AndElimR
-- ⚑ WAS `import Substrate.Algebra.F2 as F2` — retired barrel + banned alias.
open import Substrate.Algebra.F2.F2
open import Substrate.Foundation.Eq
open import Substrate.Algebra.F2.Polynomial.Wedge.GUnit.Base.AllVec



all-vec-sound : {n : ℕ} (P : Vec F₂ n → Bool) → all-vec P ≡ true
              → (v : Vec F₂ n) → P v ≡ true
all-vec-sound {zero}  P h []         = h
all-vec-sound {suc n} P h (𝟘 ∷ v) = all-vec-sound (λ w → P (𝟘 ∷ w)) (∧-elimˡ {all-vec (λ w → P (𝟘 ∷ w))} h) v
all-vec-sound {suc n} P h (𝟙 ∷ v) = all-vec-sound (λ w → P (𝟙 ∷ w)) (∧-elimʳ {all-vec (λ w → P (𝟘 ∷ w))} h) v
