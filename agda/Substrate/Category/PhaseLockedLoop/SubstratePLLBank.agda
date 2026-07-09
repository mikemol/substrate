------------------------------------------------------------------------
-- Substrate.Category.PhaseLockedLoop.SubstratePLLBank
--
-- The substrate-aligned PLL bank: a list of Sylow primes, one
-- 3-cycle strategy per prime. The substrate-4prime-bank uses
-- {2, 3, 5, 7} as the canonical GL(4, F₂) Sylow set.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Category.PhaseLockedLoop.SubstratePLLBank where

open import Substrate.Foundation.Nat using (ℕ)
open import Substrate.Foundation.List using (List; []; _∷_)

open import Substrate.Category.PhaseLockedLoop.AcquisitionStrategies
  using (ThreeCycleStrategy; mkThreeCycle)

-- ⟡set1-paydown: this record fields only `primes : List ℕ` and `strategy : List
-- ThreeCycleStrategy` (both Set-valued; ThreeCycleStrategy : Set), so it inhabits Set —
-- the Set₂ annotation was gratuitous.
record SubstratePLLBank : Set where
  field
    primes   : List ℕ
    strategy : List ThreeCycleStrategy

open SubstratePLLBank public

substrate-4prime-bank : SubstratePLLBank
substrate-4prime-bank = record
  { primes   = 2 ∷ 3 ∷ 5 ∷ 7 ∷ []
  ; strategy = mkThreeCycle 2
               ∷ mkThreeCycle 3
               ∷ mkThreeCycle 5
               ∷ mkThreeCycle 7
               ∷ []
  }
