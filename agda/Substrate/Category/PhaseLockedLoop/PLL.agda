------------------------------------------------------------------------
-- Substrate.Category.PhaseLockedLoop.PLL
--
-- The PLL primitive record. Parameterised over reference signal and
-- VCO state types; concrete instances supply the phase-error metric,
-- VCO update, and lock detector.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Category.PhaseLockedLoop.PLL where

open import Substrate.Foundation.Nat using (ℕ)
open import Substrate.Foundation.Bool using (Bool)

record PLL : Set₁ where
  field
    Reference   : Set
    VCOState    : Set
    initial-vco : VCOState
    phase-error : Reference → VCOState → ℕ
    update-vco  : VCOState → Reference → VCOState
    lock-test   : ℕ → Bool

open PLL public
