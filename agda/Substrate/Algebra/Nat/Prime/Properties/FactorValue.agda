------------------------------------------------------------------------
-- Substrate.Algebra.Nat.Prime.Properties.FactorValue
--
-- Defines: factor-value
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.Algebra.Nat.Prime.Properties; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.Nat.Prime.Properties.FactorValue where

open import Substrate.Foundation.Nat.Nat
open import Substrate.Foundation.List
open import Substrate.Algebra.Nat.DivMod.Unique.Private
open import Substrate.Algebra.Nat.WellFounded.Private
open import Substrate.Algebra.Nat.Prime
open import Substrate.Algebra.Nat.Prime.Properties.Pred



-- F : the carrier value (positive n ↦ n−1, so the retraction is total on ℕ).
factor-value : List ℕ → ℕ
factor-value ps = pred (product ps)
