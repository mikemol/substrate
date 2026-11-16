------------------------------------------------------------------------
-- Substrate.Algebra.Z.Properties.MulFull.TimesIntCancelRPos
--
-- Defines: *ℤ-cancelʳ-pos
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.Algebra.Z.Properties.MulFull; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.Z.Properties.MulFull.TimesIntCancelRPos where

open import Substrate.Foundation.Nat.Nat
open import Substrate.Foundation.Nat.Plus
open import Substrate.Algebra.Z.Int
open import Substrate.Algebra.Z.Mul
open import Substrate.Foundation.Nat.Properties.Cancel.PlusCancelL
open import Substrate.Foundation.Nat.Properties.Cancel.TimesCancelRSuc   ------------------------------------------------------------------------
open import Substrate.Algebra.Z.Properties.MulFull.PlusIntInjective
open import Substrate.Algebra.Z.Properties.MulFull.SucInjectiveInt
open import Substrate.Foundation.Eq
open import Substrate.Foundation.Eq.Cong



*ℤ-cancelʳ-pos : (x y : ℤ) (d : ℕ) →
                 x *ℤ (+ suc d) ≡ y *ℤ (+ suc d) → x ≡ y
*ℤ-cancelʳ-pos (+ m)    (+ n)    d eq = cong +_ (*-cancelʳ-suc m n d (+ℤ-injective eq))
*ℤ-cancelʳ-pos (+ m)    (-suc n) d ()
*ℤ-cancelʳ-pos (-suc m) (+ n)    d ()
*ℤ-cancelʳ-pos (-suc m) (-suc n) d eq =
  cong -suc_ (*-cancelʳ-suc m n d (+-cancelˡ d (-suc-injectiveℤ eq)))
