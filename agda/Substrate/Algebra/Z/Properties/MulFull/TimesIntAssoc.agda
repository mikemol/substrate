------------------------------------------------------------------------
-- Substrate.Algebra.Z.Properties.MulFull.TimesIntAssoc
--
-- Defines: *ℤ-assoc
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.Algebra.Z.Properties.MulFull; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.Z.Properties.MulFull.TimesIntAssoc where

open import Substrate.Foundation.Nat.Nat
open import Substrate.Foundation.Nat.Plus
open import Substrate.Foundation.Nat.Times
open import Substrate.Algebra.Z.Int
open import Substrate.Algebra.Z.Int2
open import Substrate.Algebra.Z.IntInvolutive
open import Substrate.Algebra.Z.Int2
open import Substrate.Algebra.Z.IntInvolutive
open import Substrate.Algebra.Z.Mul
open import Substrate.Algebra.Z.Sub
open import Substrate.Algebra.Z.Properties.Mul
open import Substrate.Algebra.Z.Properties.MulFull.NegTimesRight
open import Substrate.Foundation.Eq
open import Substrate.Foundation.Eq.Cong
open import Substrate.Foundation.Eq.Sym
open import Substrate.Foundation.Eq.Trans



------------------------------------------------------------------------
-- 3. Full associativity (all sign cases), reducing to *ℤ-assoc-pos-pos.
------------------------------------------------------------------------

*ℤ-assoc : (x y z : ℤ) → (x *ℤ y) *ℤ z ≡ x *ℤ (y *ℤ z)
*ℤ-assoc x (+ j) (+ k)       = *ℤ-assoc-pos-pos x j k
*ℤ-assoc x (+ j) (-suc k)    =
  trans (neg-*-right (x *ℤ (+ j)) (+ suc k))
        (trans (cong -ℤ_ (*ℤ-assoc-pos-pos x j (suc k)))
               (sym (neg-*-right x (+ (j * suc k)))))
*ℤ-assoc x (-suc j) (+ k)    =
  trans (cong (_*ℤ (+ k)) (neg-*-right x (+ suc j)))
        (trans (neg-*-left (x *ℤ (+ suc j)) (+ k))
               (trans (cong -ℤ_ (*ℤ-assoc-pos-pos x (suc j) k))
                      (sym (neg-*-right x (+ (suc j * k))))))
*ℤ-assoc x (-suc j) (-suc k) =
  trans (cong (_*ℤ (-suc k)) (neg-*-right x (+ suc j)))
        (trans (neg-*-right (-ℤ (x *ℤ (+ suc j))) (+ suc k))
               (trans (cong -ℤ_ (neg-*-left (x *ℤ (+ suc j)) (+ suc k)))
                      (trans (-ℤ-involutive ((x *ℤ (+ suc j)) *ℤ (+ suc k)))
                             (*ℤ-assoc-pos-pos x (suc j) (suc k)))))
