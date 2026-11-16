------------------------------------------------------------------------
-- Substrate.Algebra.Nat.GCD.LcmN
--
-- lcm-ℕ : ℕ → ℕ → ℕ. Loose-bound LCM = a * b. Structurally divisible
-- by both a and b. Tighter `lcm = a * b / gcd` deferred (requires
-- NonZero handling for gcd).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.Nat.GCD.LcmN where

open import Substrate.Foundation.Nat.Nat
open import Substrate.Foundation.Nat.Times

lcm-ℕ : ℕ → ℕ → ℕ
lcm-ℕ a b = a * b
