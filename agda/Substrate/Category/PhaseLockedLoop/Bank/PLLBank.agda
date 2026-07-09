------------------------------------------------------------------------
-- Substrate.Category.PhaseLockedLoop.Bank.PLLBank
--
-- Polyphonic PLL bank: a (substrate-Word) list of primes plus
-- per-prime PLL + lock-state lookups.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Category.PhaseLockedLoop.Bank.PLLBank where

open import Substrate.Foundation.Nat using (ℕ)
open import Substrate.Groups.Coxeter.Word using (Word)

open import Substrate.Category.PhaseLockedLoop.LockState using (LockState)
open import Substrate.Category.PhaseLockedLoop.PLL using (PLL)

-- ⟡set1-paydown: parameterize the per-prime carrier families Reference, VCOState :
-- ℕ → Set out of the record (substrate stance: families are module params, never
-- fields). With PLL : Set they were the only Set₁ source, so the record drops from
-- Set₁ to Set; consumers write `PLLBank Reference VCOState`.
module _ (Reference VCOState : ℕ → Set) where
  record PLLBank : Set where     -- was : Set₁
    field
      primes        : Word ℕ
      pll-at        : (p : ℕ) → PLL (Reference p) (VCOState p)
      lock-state-at : ℕ → LockState

  open PLLBank public
