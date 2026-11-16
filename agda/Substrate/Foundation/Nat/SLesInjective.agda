------------------------------------------------------------------------
-- Substrate.Foundation.Nat.SLesInjective
--
-- Defines: s≤s-injective
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.Foundation.Nat; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Foundation.Nat.SLesInjective where

open import Substrate.Foundation.Nat.Nat
open import Substrate.Foundation.Nat.Le



s≤s-injective : {m n : ℕ} → suc m ≤ suc n → m ≤ n
s≤s-injective (s≤s p) = p
