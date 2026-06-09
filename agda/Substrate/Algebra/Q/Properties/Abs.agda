------------------------------------------------------------------------
-- Substrate.Algebra.Q.Properties.Abs
--
-- Absolute-value / sign bookkeeping for the ℚ-Canonical capstone:
--
--   abs-neg-pos : abs-ℤ (-ℤ (+ k)) ≡ k
--   abs-sign-of : abs-ℤ (sign-of z n) ≡ n          (reduce's magnitude)
--   abs-*ℤ-pos  : abs-ℤ (z *ℤ (+ suc n)) ≡ abs-ℤ z * suc n   (cross-mult magnitude)
--   ℤ-sign-mag  : a positive-denominator cross-mult equation + equal magnitude
--                 ⟹ equal ℤ (sign agreement, cross cases by constructor clash)
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.Q.Properties.Abs where

open import Substrate.Foundation.Nat using (ℕ; zero; suc; _*_)
open import Substrate.Foundation.Nat.Properties.Cancel using (suc-injective)
open import Substrate.Foundation.Eq using (_≡_; refl; cong)
open import Substrate.Algebra.Z using (ℤ; +_; -suc_; -ℤ_)
open import Substrate.Algebra.Z.Arithmetic using (_*ℤ_)
open import Substrate.Algebra.Q.Reduce using (sign-of)
open import Substrate.Algebra.Q.Reduction using (abs-ℤ)

abs-neg-pos : (k : ℕ) → abs-ℤ (-ℤ (+ k)) ≡ k
abs-neg-pos zero    = refl
abs-neg-pos (suc j) = refl

abs-sign-of : (z : ℤ) (n : ℕ) → abs-ℤ (sign-of z n) ≡ n
abs-sign-of (+ _)    n = refl
abs-sign-of (-suc _) n = abs-neg-pos n

abs-*ℤ-pos : (z : ℤ) (n : ℕ) → abs-ℤ (z *ℤ (+ suc n)) ≡ abs-ℤ z * suc n
abs-*ℤ-pos (+ m)    n = refl
abs-*ℤ-pos (-suc m) n = abs-neg-pos (suc m * suc n)

-- Sign agreement: equal cross-products (positive denominators) + equal
-- magnitude pin the ℤ. Cross-sign cases are refuted by the +/-suc clash.
ℤ-sign-mag : (x y : ℤ) (d e : ℕ) →
  x *ℤ (+ suc d) ≡ y *ℤ (+ suc e) → abs-ℤ x ≡ abs-ℤ y → x ≡ y
ℤ-sign-mag (+ mx)    (+ my)    d e _  mag = cong +_ mag
ℤ-sign-mag (+ mx)    (-suc my) d e () _
ℤ-sign-mag (-suc mx) (+ my)    d e () _
ℤ-sign-mag (-suc mx) (-suc my) d e _  mag = cong -suc_ (suc-injective mag)
