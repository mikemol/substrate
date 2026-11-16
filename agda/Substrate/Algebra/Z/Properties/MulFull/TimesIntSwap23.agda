------------------------------------------------------------------------
-- Substrate.Algebra.Z.Properties.MulFull.TimesIntSwap23
--
-- Defines: *ℤ-swap₂₃
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.Algebra.Z.Properties.MulFull; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.Z.Properties.MulFull.TimesIntSwap23 where

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
open import Substrate.Algebra.Z.Properties.Mul
open import Substrate.Algebra.Z.Properties.MulFull.TimesIntAssoc
open import Substrate.Foundation.Eq
open import Substrate.Foundation.Eq.Cong
open import Substrate.Foundation.Eq.Sym
open import Substrate.Foundation.Eq.Trans



-- swap the last two factors: (x·y)·z ≡ (x·z)·y.
*ℤ-swap₂₃ : (x y z : ℤ) → (x *ℤ y) *ℤ z ≡ (x *ℤ z) *ℤ y
*ℤ-swap₂₃ x y z =
  trans (*ℤ-assoc x y z)
        (trans (cong (x *ℤ_) (*ℤ-comm y z)) (sym (*ℤ-assoc x z y)))
