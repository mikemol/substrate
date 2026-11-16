------------------------------------------------------------------------
-- Substrate.Foundation.Nat.Properties.Sub.MMonusmEq0
--
-- Defines: m∸m≡0
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.Foundation.Nat.Properties.Sub; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Foundation.Nat.Properties.Sub.MMonusmEq0 where

open import Substrate.Foundation.Nat.Monus
open import Substrate.Foundation.Nat.Nat
open import Substrate.Foundation.Eq
-- m∸m≡0 : truncated subtraction of self is zero.
------------------------------------------------------------------------

m∸m≡0 : (m : ℕ) → m ∸ m ≡ 0
m∸m≡0 zero    = refl
m∸m≡0 (suc m) = m∸m≡0 m
