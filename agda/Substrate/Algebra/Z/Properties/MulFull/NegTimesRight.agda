------------------------------------------------------------------------
-- Substrate.Algebra.Z.Properties.MulFull.NegTimesRight
--
-- Defines: neg-*-right
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.Algebra.Z.Properties.MulFull; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.Z.Properties.MulFull.NegTimesRight where

open import Substrate.Algebra.Z.DecInt
open import Substrate.Algebra.Z.DecInt
open import Substrate.Algebra.Z.Int
open import Substrate.Algebra.Z.Int2
open import Substrate.Algebra.Z.IntInvolutive
open import Substrate.Algebra.Z.NatDec
open import Substrate.Algebra.Z.OneInt
open import Substrate.Algebra.Z.OneInt2
open import Substrate.Algebra.Z.ZeroInt
open import Substrate.Algebra.Z.Int2
open import Substrate.Algebra.Z.IntInvolutive
open import Substrate.Algebra.Z.NatDec
open import Substrate.Algebra.Z.OneInt
open import Substrate.Algebra.Z.OneInt2
open import Substrate.Algebra.Z.ZeroInt
open import Substrate.Algebra.Z.Mul
open import Substrate.Algebra.Z.Sub
open import Substrate.Algebra.Z.Properties.Mul
open import Substrate.Foundation.Eq
open import Substrate.Foundation.Eq.Cong
open import Substrate.Foundation.Eq.Trans


-- 1. Negation pulls out of the right factor too.
------------------------------------------------------------------------

neg-*-right : (x y : ℤ) → x *ℤ (-ℤ y) ≡ -ℤ (x *ℤ y)
neg-*-right x y =
  trans (*ℤ-comm x (-ℤ y))
        (trans (neg-*-left y x) (cong -ℤ_ (*ℤ-comm y x)))
