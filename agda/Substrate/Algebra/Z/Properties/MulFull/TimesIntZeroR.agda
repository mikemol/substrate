------------------------------------------------------------------------
-- Substrate.Algebra.Z.Properties.MulFull.TimesIntZeroR
--
-- Defines: *ℤ-zeroʳ
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.Algebra.Z.Properties.MulFull; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.Z.Properties.MulFull.TimesIntZeroR where

open import Substrate.Foundation.Nat.Nat
open import Substrate.Foundation.Nat.Plus
open import Substrate.Foundation.Nat.Properties.Mul.TimesZeroR
open import Substrate.Algebra.Z.Int
open import Substrate.Algebra.Z.Int2
open import Substrate.Algebra.Z.Int2
open import Substrate.Algebra.Z.Mul
open import Substrate.Algebra.Z.Sub
open import Substrate.Foundation.Eq
open import Substrate.Foundation.Eq.Cong



*ℤ-zeroʳ : (x : ℤ) → x *ℤ (+ 0) ≡ + 0
*ℤ-zeroʳ (+ m)    = cong +_ (*-zeroʳ m)
*ℤ-zeroʳ (-suc m) = cong (λ z → -ℤ (+ z)) (*-zeroʳ (suc m))
