------------------------------------------------------------------------
-- Substrate.Algebra.CayleyDickson.Setoid
--
-- The `≈#` equivalence on the Cayley-Dickson tower, plus the `neg`/`conj`
-- behaviour on `zero#` — the setoid infrastructure that CD reasoning (and in
-- particular the ⊙.morton cocycle: conj-on-basis, the recursive product law)
-- needs but `Algebra.CayleyDickson` did not yet have (it carried only the bare
-- `i²≈−1` and the zero-divisor projections). Everything is structural induction
-- on the level `n`, bottoming out in ℚ's setoid (`≈# 0 = ≈ℚ`).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.CayleyDickson.Setoid where

open import Substrate.Foundation.Nat using (ℕ; zero; suc)
open import Substrate.Foundation.Eq using (refl)
open import Substrate.Foundation.Product using (_,_; _×_)
open import Substrate.Algebra.Q.Equiv using (_≈ℚ_; ≈ℚ-refl; ≈ℚ-sym; ≈ℚ-trans)
open import Substrate.Algebra.CayleyDickson using (Carrier; ≈#; neg; conj; zero#)

------------------------------------------------------------------------
-- 1. ≈# is an equivalence (componentwise lift of ℚ's setoid).
------------------------------------------------------------------------

≈#-refl : (n : ℕ) (x : Carrier n) → ≈# n x x
≈#-refl zero    x       = ≈ℚ-refl x
≈#-refl (suc n) (a , b) = ≈#-refl n a , ≈#-refl n b

≈#-sym : (n : ℕ) {x y : Carrier n} → ≈# n x y → ≈# n y x
≈#-sym zero    {x} {y} p       = ≈ℚ-sym {x} {y} p
≈#-sym (suc n) (p , q)         = ≈#-sym n p , ≈#-sym n q

≈#-trans : (n : ℕ) {x y z : Carrier n} → ≈# n x y → ≈# n y z → ≈# n x z
≈#-trans zero    {x} {y} {z} p r = ≈ℚ-trans {x} {y} {z} p r
≈#-trans (suc n) (p , q) (p′ , q′) = ≈#-trans n p p′ , ≈#-trans n q q′

------------------------------------------------------------------------
-- 2. neg and conj fix zero# (the doubling's empty residue).
------------------------------------------------------------------------

-- neg n (zero# n) ≈# zero# n.  (At ℚ, −0 = 0 — by the ℤ zero self-negation.)
neg-zero# : (n : ℕ) → ≈# n (neg n (zero# n)) (zero# n)
neg-zero# zero    = refl
neg-zero# (suc n) = neg-zero# n , neg-zero# n

-- conj n (zero# n) ≈# zero# n.  (conj fixes the all-zero vector.)
conj-zero# : (n : ℕ) → ≈# n (conj n (zero# n)) (zero# n)
conj-zero# zero    = refl
conj-zero# (suc n) = conj-zero# n , neg-zero# n
