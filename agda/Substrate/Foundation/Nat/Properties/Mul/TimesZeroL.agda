------------------------------------------------------------------------
-- Substrate.Foundation.Nat.Properties.Mul.TimesZeroL
--
-- Defines: *-zeroˡ
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.Foundation.Nat.Properties.Mul; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Foundation.Nat.Properties.Mul.TimesZeroL where

open import Substrate.Foundation.Nat.Nat
open import Substrate.Foundation.Nat.Times
open import Substrate.Foundation.Eq



*-zeroˡ : (n : ℕ) → zero * n ≡ zero
*-zeroˡ _ = refl
