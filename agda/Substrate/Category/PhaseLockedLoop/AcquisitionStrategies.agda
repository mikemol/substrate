------------------------------------------------------------------------
-- Substrate.Category.PhaseLockedLoop.AcquisitionStrategies
--
-- Three acquisition strategies for PLL lock acquisition:
--   ThreeCycleStrategy: activate at 3·prime samples
--   CostGateStrategy: sustained cost-gate inequality over a window
--   WarmupBufferStrategy: acquisition aid + cost gate
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Category.PhaseLockedLoop.AcquisitionStrategies where

open import Substrate.Foundation.Nat using (ℕ; _*_)
open import Substrate.Foundation.Eq using (_≡_; refl)

------------------------------------------------------------------------
-- Strategy A: 3-cycle capture.

record ThreeCycleStrategy : Set where
  field
    prime          : ℕ
    activation-pos : ℕ
    rule           : activation-pos ≡ 3 * prime

open ThreeCycleStrategy public

mkThreeCycle : (p : ℕ) → ThreeCycleStrategy
mkThreeCycle p = record { prime = p ; activation-pos = 3 * p ; rule = refl }

------------------------------------------------------------------------
-- Strategy B: cost-gate lock detector.

record CostGateStrategy : Set where
  field
    prime       : ℕ
    window-size : ℕ

open CostGateStrategy public

------------------------------------------------------------------------
-- Strategy C: warmup-buffer + cost gate.

record WarmupBufferStrategy : Set where
  field
    prime        : ℕ
    aid-position : ℕ
    gate-window  : ℕ

open WarmupBufferStrategy public

mkWarmupBuffer : (p : ℕ) → ℕ → ℕ → WarmupBufferStrategy
mkWarmupBuffer p aid window = record
  { prime = p ; aid-position = aid ; gate-window = window }
