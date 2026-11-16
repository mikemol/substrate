------------------------------------------------------------------------
-- Substrate.Algebra.Z.Properties.MulFull.TimesIntDistribRPlus
--
-- Defines: *ℤ-distribʳ-+
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.Algebra.Z.Properties.MulFull; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.Z.Properties.MulFull.TimesIntDistribRPlus where

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
open import Substrate.Algebra.Z.Add.PlusInt
open import Substrate.Algebra.Z.Mul
open import Substrate.Algebra.Z.Properties.Mul
open import Substrate.Algebra.Z.Properties.MulFull.TimesIntDistribLPlus
open import Substrate.Foundation.Eq
open import Substrate.Foundation.Eq.Cong2
open import Substrate.Foundation.Eq.Trans



*ℤ-distribʳ-+ : (x y z : ℤ) → (x +ℤ y) *ℤ z ≡ (x *ℤ z) +ℤ (y *ℤ z)
*ℤ-distribʳ-+ x y z =
  trans (*ℤ-comm (x +ℤ y) z)
        (trans (*ℤ-distribˡ-+ z x y)
               (cong₂ _+ℤ_ (*ℤ-comm z x) (*ℤ-comm z y)))
