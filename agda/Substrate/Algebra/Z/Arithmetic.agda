------------------------------------------------------------------------
-- Substrate.Algebra.Z.Arithmetic
--
-- ℤ arithmetic — the operand type for "changing the types" that EEA
-- operates on. Definitions only (laws live in Z.Properties per the
-- def/proof separation policy). Addition routes through the truncated
-- difference _⊖_ : ℕ → ℕ → ℤ (the one place sign appears); multiplication
-- is sign-magnitude on the two-constructor (+_ / -suc_) form.
--
-- Why ℤ: the Bézout bridge s·a + t·b = gcd has SIGNED coefficients; over
-- ℤ the Euclidean back-substitution is clean ring algebra (no ℕ-balanced
-- sign-tag case-split). See scratch plan + [[project_center_free_universal_property]].
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.Z.Arithmetic where

open import Substrate.Foundation.Nat using (ℕ; zero; suc; _+_; _*_)
open import Substrate.Algebra.Z using (ℤ; +_; -suc_; -ℤ_; 0ℤ; 1ℤ)

infixl 6 _+ℤ_ _-ℤ_ _⊖_
infixl 7 _*ℤ_

-- truncated difference of two naturals AS an integer: m ⊖ n = m − n.
_⊖_ : ℕ → ℕ → ℤ
m     ⊖ zero  = + m
zero  ⊖ suc n = -suc n
suc m ⊖ suc n = m ⊖ n

-- integer addition.
_+ℤ_ : ℤ → ℤ → ℤ
(+ m)    +ℤ (+ n)    = + (m + n)
(+ m)    +ℤ (-suc n) = m ⊖ suc n
(-suc m) +ℤ (+ n)    = n ⊖ suc m
(-suc m) +ℤ (-suc n) = -suc suc (m + n)

-- integer subtraction.
_-ℤ_ : ℤ → ℤ → ℤ
a -ℤ b = a +ℤ (-ℤ b)

-- integer multiplication (sign-magnitude).
_*ℤ_ : ℤ → ℤ → ℤ
(+ m)    *ℤ (+ n)    = + (m * n)
(+ m)    *ℤ (-suc n) = -ℤ (+ (m * suc n))
(-suc m) *ℤ (+ n)    = -ℤ (+ (suc m * n))
(-suc m) *ℤ (-suc n) = + (suc m * suc n)
