------------------------------------------------------------------------
-- Substrate.Algebra.Z.Add
--
-- ℤ addition `_+ℤ_`, routed through the truncated difference `_⊖_ : ℕ → ℕ → ℤ`
-- (the one place sign appears). One canonical operator per file
-- (carrier-locality policy; see scratch/carrier_locality_policy.md). The `⊖`
-- helper lives here because `_+ℤ_` is its sole caller-shape.
--
-- Definitions only (laws live in Z.Properties). Re-exported by
-- Substrate.Algebra.Z.Arithmetic.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.Z.Add where

open import Substrate.Foundation.Nat using (ℕ; zero; suc; _+_)
open import Substrate.Algebra.Z using (ℤ; +_; -suc_)

infixl 6 _+ℤ_ _⊖_

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
