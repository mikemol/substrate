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

-- ⟡set1-paydown: parameterize Reference and VCOState. Both were carrier FIELDS
-- (`Reference/VCOState : Set`), forcing PLL : Set₁; take them as module parameters
-- and every field is Set-valued, so PLL : Set. Consumers write `PLL Reference VCOState`.
module _ (Reference VCOState : Set) where
  record PLL : Set where     -- was : Set₁
    field
      initial-vco : VCOState
      phase-error : Reference → VCOState → ℕ
      update-vco  : VCOState → Reference → VCOState
      lock-test   : ℕ → Bool

  open PLL public
