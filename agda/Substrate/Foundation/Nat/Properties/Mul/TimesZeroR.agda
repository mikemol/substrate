------------------------------------------------------------------------
-- Substrate.Foundation.Nat.Properties.Mul.TimesZeroR
--
-- Defines: *-zeroʳ
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.Foundation.Nat.Properties.Mul; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Foundation.Nat.Properties.Mul.TimesZeroR where

open import Substrate.Foundation.Nat.Nat
open import Substrate.Foundation.Nat.Times
open import Substrate.Foundation.Eq



*-zeroʳ : (n : ℕ) → n * zero ≡ zero
*-zeroʳ zero    = refl
*-zeroʳ (suc n) = *-zeroʳ n
