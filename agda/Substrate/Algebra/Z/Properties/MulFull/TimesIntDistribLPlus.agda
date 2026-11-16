------------------------------------------------------------------------
-- Substrate.Algebra.Z.Properties.MulFull.TimesIntDistribLPlus
--
-- Defines: *ℤ-distribˡ-+
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.Algebra.Z.Properties.MulFull; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.Z.Properties.MulFull.TimesIntDistribLPlus where

open import Substrate.Foundation.Nat.Nat
open import Substrate.Foundation.Nat.Plus
open import Substrate.Algebra.Z.Int
open import Substrate.Algebra.Z.Int2
open import Substrate.Algebra.Z.Int2
open import Substrate.Algebra.Z.Add.PlusInt
open import Substrate.Algebra.Z.Mul
open import Substrate.Algebra.Z.Properties.Mul
open import Substrate.Algebra.Z.Properties.MulFull.NegPlusInt
open import Substrate.Foundation.Eq
open import Substrate.Foundation.Eq.Cong
open import Substrate.Foundation.Eq.Cong2
open import Substrate.Foundation.Eq.Sym
open import Substrate.Foundation.Eq.Trans



------------------------------------------------------------------------
-- 5. Full distributivity (all sign cases).
------------------------------------------------------------------------

*ℤ-distribˡ-+ : (x y z : ℤ) → x *ℤ (y +ℤ z) ≡ (x *ℤ y) +ℤ (x *ℤ z)
*ℤ-distribˡ-+ (+ k)    y z = distribˡ-scalar k y z
*ℤ-distribˡ-+ (-suc m) y z =
  trans (neg-*-left (+ suc m) (y +ℤ z))
        (trans (cong -ℤ_ (distribˡ-scalar (suc m) y z))
               (trans (neg-+ℤ ((+ suc m) *ℤ y) ((+ suc m) *ℤ z))
                      (cong₂ _+ℤ_ (sym (neg-*-left (+ suc m) y))
                                  (sym (neg-*-left (+ suc m) z)))))
