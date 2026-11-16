------------------------------------------------------------------------
-- Substrate.Algebra.Z.Properties.MulFull.TimesIntIdentityR
--
-- Defines: *ℤ-identityʳ
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.Algebra.Z.Properties.MulFull; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.Z.Properties.MulFull.TimesIntIdentityR where

open import Substrate.Foundation.Nat.Nat
open import Substrate.Foundation.Nat.Plus
open import Substrate.Algebra.Z.Int
open import Substrate.Algebra.Z.Int2
open import Substrate.Algebra.Z.Int2
open import Substrate.Algebra.Z.Mul
open import Substrate.Algebra.Z.Properties.Mul
open import Substrate.Algebra.Z.Properties.MulFull.TimesIntIdentityL
open import Substrate.Foundation.Eq
open import Substrate.Foundation.Eq.Trans



*ℤ-identityʳ : (x : ℤ) → x *ℤ (+ 1) ≡ x
*ℤ-identityʳ x = trans (*ℤ-comm x (+ 1)) (*ℤ-identityˡ x)
