------------------------------------------------------------------------
-- Substrate.Foundation.Nat.Properties.Mul.TimesComm
--
-- Defines: *-comm
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.Foundation.Nat.Properties.Mul; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Foundation.Nat.Properties.Mul.TimesComm where

open import Substrate.Foundation.Nat.Nat
open import Substrate.Foundation.Nat.Plus
open import Substrate.Foundation.Nat.Times
open import Substrate.Foundation.Nat.Properties.Mul.TimesZeroR
open import Substrate.Foundation.Nat.Properties.Mul.TimesSuc
open import Substrate.Foundation.Eq
open import Substrate.Foundation.Eq.CongTrans
open import Substrate.Foundation.Eq.Sym



*-comm : (m n : ℕ) → m * n ≡ n * m
*-comm zero    n = sym (*-zeroʳ n)
*-comm (suc m) n = cong-trans (n ℕ+_) (*-comm m n) (sym (*-suc n m))
