------------------------------------------------------------------------
-- Substrate.Foundation.Nat.Properties.SubMul.ZeroMonusn
--
-- Defines: 0∸n
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.Foundation.Nat.Properties.SubMul; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Foundation.Nat.Properties.SubMul.ZeroMonusn where

open import Substrate.Foundation.Nat.Monus
open import Substrate.Foundation.Nat.Nat
open import Substrate.Foundation.Eq
0∸n : (n : ℕ) → zero ∸ n ≡ zero
0∸n zero    = refl
0∸n (suc n) = refl
