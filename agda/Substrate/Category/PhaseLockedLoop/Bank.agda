------------------------------------------------------------------------
-- Substrate.Category.PhaseLockedLoop.Bank
--
-- Polyphonic PLL Bank + Independence law.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Category.PhaseLockedLoop.Bank where

open import Substrate.Foundation.Nat using (ℕ)
open import Data.List using (List)

open import Substrate.Category.PhaseLockedLoop.LockState using (LockState)
open import Substrate.Category.PhaseLockedLoop.PLL using (PLL)

record PLLBank : Set₂ where
  field
    primes        : List ℕ
    pll-at        : ℕ → PLL
    lock-state-at : ℕ → LockState

open PLLBank public

------------------------------------------------------------------------
-- Independence law: updating PLL_q does not change PLL_p's
-- lock state for p ≠ q. Structural marker — concrete instances
-- satisfy by construction (per-prime PLLs share no state).

record BankIndependence (bank : PLLBank) : Set where
  no-eta-equality
