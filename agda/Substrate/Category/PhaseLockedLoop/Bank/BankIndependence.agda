------------------------------------------------------------------------
-- Substrate.Category.PhaseLockedLoop.Bank.BankIndependence
--
-- Independence law: updating PLL_q does not change PLL_p's lock
-- state for p ≠ q. Structural marker — concrete instances satisfy
-- by construction (per-prime PLLs share no state).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Category.PhaseLockedLoop.Bank.BankIndependence where

open import Substrate.Foundation.Nat using (ℕ)
open import Substrate.Category.PhaseLockedLoop.Bank.PLLBank using (PLLBank)

-- ⟡set1-paydown: PLLBank now parameterizes its Reference/VCOState carrier families,
-- so this module threads them as params (`PLLBank Reference VCOState`).
module _ (Reference VCOState : ℕ → Set) where
  record BankIndependence (bank : PLLBank Reference VCOState) : Set where
    no-eta-equality
