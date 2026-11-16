------------------------------------------------------------------------
-- Substrate.Foundation.Nat.Properties.Mul.TimesAssoc
--
-- Defines: *-assoc
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.Foundation.Nat.Properties.Mul; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Foundation.Nat.Properties.Mul.TimesAssoc where

open import Substrate.Foundation.Nat.Nat
open import Substrate.Foundation.Nat.Plus
open import Substrate.Foundation.Nat.Times
open import Substrate.Foundation.Nat.Properties.Mul.TimesDistribRPlus
open import Substrate.Foundation.Eq
open import Substrate.Foundation.Eq.Cong
open import Substrate.Foundation.Eq.Trans



------------------------------------------------------------------------
-- Associativity. Reduce on the leftmost factor via *-distribʳ-+.
------------------------------------------------------------------------

*-assoc : (m n p : ℕ) → (m * n) * p ≡ m * (n * p)
*-assoc zero    _ _ = refl
*-assoc (suc m) n p =
  trans (*-distribʳ-+ p n (m * n))
        (cong (n * p ℕ+_) (*-assoc m n p))
