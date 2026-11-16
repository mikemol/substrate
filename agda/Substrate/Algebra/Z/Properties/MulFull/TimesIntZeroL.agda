------------------------------------------------------------------------
-- Substrate.Algebra.Z.Properties.MulFull.TimesIntZeroL
--
-- Defines: *ℤ-zeroˡ
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.Algebra.Z.Properties.MulFull; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.Z.Properties.MulFull.TimesIntZeroL where

open import Substrate.Foundation.Nat.Plus
open import Substrate.Algebra.Z.Int
open import Substrate.Algebra.Z.Mul
open import Substrate.Foundation.Eq



*ℤ-zeroˡ : (x : ℤ) → (+ 0) *ℤ x ≡ + 0
*ℤ-zeroˡ (+ n)    = refl
*ℤ-zeroˡ (-suc n) = refl
