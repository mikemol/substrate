------------------------------------------------------------------------
-- Substrate.Algebra.F2.Polynomial.Wedge.XPower
--
-- x-power: shift a polynomial up by d positions (multiply by xᵈ).
-- Iterated x-shift. Used by long-division's single-step reduction
-- to align q's degree with p's.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.F2.Polynomial.Wedge.XPower where

open import Substrate.Foundation.Nat using (ℕ; zero; suc) renaming (_+_ to _ℕ+_)
open import Substrate.Algebra.F2.Polynomial using (Polynomial; x-shift)

x-power : ∀ {n} (d : ℕ) → Polynomial n → Polynomial (d ℕ+ n)
x-power zero    p = p
x-power (suc d) p = x-shift (x-power d p)
