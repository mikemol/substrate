------------------------------------------------------------------------
-- Substrate.Category.PhaseLockedLoop.LoopParameters
--
-- Loop bandwidth and damping ratio (classical PLL theory). The
-- substrate's analog of loop bandwidth is the Laplace smoothing
-- parameter α — smaller α = wider bandwidth (faster adaptation,
-- more variance).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Category.PhaseLockedLoop.LoopParameters where

open import Substrate.Foundation.Nat using (ℕ)

record LoopParameters : Set where
  field
    alpha-numerator   : ℕ
    alpha-denominator : ℕ
    -- Currently 1st-order; 2nd-order with damping ratio when
    -- reference drifts.

open LoopParameters public
