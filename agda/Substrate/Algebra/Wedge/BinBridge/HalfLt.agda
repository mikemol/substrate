------------------------------------------------------------------------
-- Halving strictly shrinks a bound: the descent that makes the encoder's
-- fuel sufficient. The ≤-inversion is Foundation.Nat.s≤s-injective —
-- reused, not re-rolled as a `where`-local.
-- Context: Substrate/Algebra/Wedge/BinBridge/README.md
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.Wedge.BinBridge.HalfLt where

open import Substrate.Foundation.Nat.Le
open import Substrate.Foundation.Nat.Lt
open import Substrate.Foundation.Nat.Nat
open import Substrate.Foundation.Nat.Plus
open import Substrate.Foundation.Nat.SLesInjective
open import Substrate.Foundation.Nat.Properties.Add.PlusSuc
open import Substrate.Algebra.Wedge.BinBridge.Half
open import Substrate.Foundation.Eq.Subst

half-lt : (n k : ℕ) → n < (k ℕ+ k) → half n < k
half-lt _             zero    ()
half-lt zero          (suc _) _ = s≤s z≤n
half-lt (suc zero)    (suc _) _ = s≤s z≤n
half-lt (suc (suc n)) (suc k) (s≤s lt) =
  s≤s (half-lt n k (s≤s-injective (subst (λ z → suc (suc n) ≤ z) (+ℕ-suc k k) lt)))
