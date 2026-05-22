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

record PLLBank : Set₂ where
  field
    primes        : Word ℕ
    pll-at        : ℕ → PLL
    lock-state-at : ℕ → LockState

open PLLBank public
