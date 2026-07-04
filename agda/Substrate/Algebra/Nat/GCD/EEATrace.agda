------------------------------------------------------------------------
-- Substrate.Algebra.Nat.GCD.EEATrace
--
-- EEATrace a b g : the structural recursion of the Euclidean algorithm.
-- Asserts gcd(a, b) = g via a chain of Wedge steps.
--
--   base : gcd(a, 0) = a (terminating case).
--   step : if (a, suc b) wedges to (q, r) with r < suc b, and we
--          have EEATrace (suc b) r g, then EEATrace a (suc b) g.
--
-- All downstream properties prove via structural induction on this
-- data type.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.Nat.GCD.EEATrace where

open import Substrate.Foundation.Nat using (ℕ; suc)
open import Substrate.Algebra.Nat.GCD.Wedge using (remainder) renaming (Wedge to Wedge⟦b7e6a995⟧)
data EEATrace : ℕ → ℕ → ℕ → Set where
  base : ∀ a → EEATrace a 0 a
  step : ∀ {a g} (b : ℕ) (w : Wedge⟦b7e6a995⟧ a (suc b)) →
         EEATrace (suc b) (remainder w) g →
         EEATrace a (suc b) g
