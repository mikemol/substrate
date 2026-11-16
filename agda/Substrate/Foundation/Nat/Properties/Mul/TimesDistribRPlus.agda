------------------------------------------------------------------------
-- Substrate.Foundation.Nat.Properties.Mul.TimesDistribRPlus
--
-- Defines: *-distribʳ-+
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.Foundation.Nat.Properties.Mul; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Foundation.Nat.Properties.Mul.TimesDistribRPlus where

open import Substrate.Foundation.Nat.Nat
open import Substrate.Foundation.Nat.Plus
open import Substrate.Foundation.Nat.Times
open import Substrate.Foundation.Nat.Properties.Mul.TimesComm
open import Substrate.Foundation.Nat.Properties.Mul.TimesDistribLPlus
open import Substrate.Foundation.Eq
open import Substrate.Foundation.Eq.Cong2
open import Substrate.Foundation.Eq.Trans



*-distribʳ-+ : (a m n : ℕ) → (m ℕ+ n) * a ≡ m * a ℕ+ n * a
*-distribʳ-+ a m n =
  trans (*-comm (m ℕ+ n) a)
  (trans (*-distribˡ-+ a m n)
         (cong₂ _ℕ+_ (*-comm a m) (*-comm a n)))
