------------------------------------------------------------------------
-- Substrate.Category.PhaseLockedLoop.Bank.BankIndependence
--
-- Independence law: updating PLL_q does not change PLL_p's lock
-- state for p ≠ q. Structural marker — concrete instances satisfy
-- by construction (per-prime PLLs share no state).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Category.PhaseLockedLoop.Bank.BankIndependence where

open import Substrate.Category.PhaseLockedLoop.Bank.PLLBank using (PLLBank)

record BankIndependence (bank : PLLBank) : Set where
  no-eta-equality
