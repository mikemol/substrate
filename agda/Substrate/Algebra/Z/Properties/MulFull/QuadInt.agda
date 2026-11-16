------------------------------------------------------------------------
-- Substrate.Algebra.Z.Properties.MulFull.QuadInt
--
-- Defines: quadℤ
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.Algebra.Z.Properties.MulFull; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.Z.Properties.MulFull.QuadInt where

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



-- middle-factor interchange of a product of two products (ℤ analogue of
-- Nat.Properties.Mul.quad); used to normalize ℚ distributivity numerators.
quadℤ : (w x y z : ℤ) → (w *ℤ x) *ℤ (y *ℤ z) ≡ (w *ℤ y) *ℤ (x *ℤ z)
quadℤ w x y z =
  trans (*ℤ-assoc w x (y *ℤ z))
  (trans (cong (w *ℤ_) (sym (*ℤ-assoc x y z)))
  (trans (cong (λ t → w *ℤ (t *ℤ z)) (*ℤ-comm x y))
  (trans (cong (w *ℤ_) (*ℤ-assoc y x z))
         (sym (*ℤ-assoc w y (x *ℤ z))))))
