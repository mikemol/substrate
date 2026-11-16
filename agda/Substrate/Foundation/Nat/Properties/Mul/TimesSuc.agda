------------------------------------------------------------------------
-- Substrate.Foundation.Nat.Properties.Mul.TimesSuc
--
-- Defines: *-suc
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.Foundation.Nat.Properties.Mul; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Foundation.Nat.Properties.Mul.TimesSuc where

open import Substrate.Foundation.Nat.Nat
open import Substrate.Foundation.Nat.Plus
open import Substrate.Foundation.Nat.Times
open import Substrate.Foundation.Nat.Properties.Add.PlusAssoc
open import Substrate.Foundation.Nat.Properties.Add.PlusComm
open import Substrate.Foundation.Eq
open import Substrate.Foundation.Eq.Cong
open import Substrate.Foundation.Eq.CongTrans
open import Substrate.Foundation.Eq.SymTrans



*-suc : (m n : ℕ) → m * suc n ≡ m ℕ+ m * n
*-suc zero    _ = refl
*-suc (suc m) n =
  cong suc
    (cong-trans (n ℕ+_) (*-suc m n)
       (sym-trans (+ℕ-assoc n m (m * n))
          (cong-trans (_ℕ+ (m * n)) (+ℕ-comm n m)
             (+ℕ-assoc m n (m * n)))))
