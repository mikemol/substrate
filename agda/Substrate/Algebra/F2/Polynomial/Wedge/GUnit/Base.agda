{-# OPTIONS --safe --without-K #-}
------------------------------------------------------------------------
-- Substrate.Algebra.F2.Polynomial.Wedge.GUnit.Base  (EEA-FREE thin slice)
--
-- The constants + exhaustion machinery of GUnit that do NOT touch the
-- fuel-EEA: the AES modulus low part `m-lo`, the zero-byte test `is-zero8`,
-- and the generic 2ⁿ bit-vector exhaustion `all-vec`/`all-vec-sound`. These
-- depend only on F2/Vec/Bool + `∧-elimˡ/ʳ` — ZERO transitive dep on
-- gcd-of/is-unit-q/fuel-bezout/QPoly/EEATrace/FuelEEA/Graded.Div. A consumer
-- that needs only these (the S-box / xtime byte tables) imports this thin base
-- instead of GUnit, shedding the EEATrace/FuelEEA closure (floor closure b).
-- GUnit itself opens `Base public`, so its EEA-side `gcd-of`/`is-unit-q`/`check`/
-- `g-unit-*` and every other consumer are unchanged. --safe --without-K, 0 postulates.
------------------------------------------------------------------------

module Substrate.Algebra.F2.Polynomial.Wedge.GUnit.Base where

open import Substrate.Foundation.Nat using (ℕ; zero; suc)
open import Substrate.Foundation.Vec using (Vec; []; _∷_)
open import Substrate.Foundation.Eq using (_≡_)
open import Substrate.Foundation.Bool using (Bool; true; false; _∧_)
open import Substrate.Foundation.Bool.Properties using (∧-elimˡ; ∧-elimʳ) public
import Substrate.Algebra.F2 as F2

-- AES modulus low part: b-poly = x^8 + x^4+x^3+x+1.
m-lo : Vec F2.F₂ 8
m-lo = F2.𝟙 ∷ F2.𝟙 ∷ F2.𝟘 ∷ F2.𝟙 ∷ F2.𝟙 ∷ F2.𝟘 ∷ F2.𝟘 ∷ F2.𝟘 ∷ []

is-zero8 : Vec F2.F₂ 8 → Bool
is-zero8 (F2.𝟘 ∷ F2.𝟘 ∷ F2.𝟘 ∷ F2.𝟘 ∷ F2.𝟘 ∷ F2.𝟘 ∷ F2.𝟘 ∷ F2.𝟘 ∷ []) = true
is-zero8 _ = false

-- generic exhaustion over all 2^n bit-vectors + soundness.
all-vec : {n : ℕ} (P : Vec F2.F₂ n → Bool) → Bool
all-vec {zero}  P = P []
all-vec {suc n} P = all-vec (λ v → P (F2.𝟘 ∷ v)) ∧ all-vec (λ v → P (F2.𝟙 ∷ v))

all-vec-sound : {n : ℕ} (P : Vec F2.F₂ n → Bool) → all-vec P ≡ true
              → (v : Vec F2.F₂ n) → P v ≡ true
all-vec-sound {zero}  P h []         = h
all-vec-sound {suc n} P h (F2.𝟘 ∷ v) = all-vec-sound (λ w → P (F2.𝟘 ∷ w)) (∧-elimˡ {all-vec (λ w → P (F2.𝟘 ∷ w))} h) v
all-vec-sound {suc n} P h (F2.𝟙 ∷ v) = all-vec-sound (λ w → P (F2.𝟙 ∷ w)) (∧-elimʳ {all-vec (λ w → P (F2.𝟘 ∷ w))} h) v
