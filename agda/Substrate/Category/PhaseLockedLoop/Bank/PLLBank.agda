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

-- ⟡set1-paydown (consumer of PLL): PLL is now carrier-parameterized (`PLL R V`), so
-- `pll-at` names each prime's Reference/VCOState via per-prime carrier families —
-- keeping PLLBank at arity 0 (so `BankIndependence (bank : PLLBank)` is unaffected).
-- With PLL : Set, the ℕ→Set carrier families are the only Set₁ source: Set₂ → Set₁.
record PLLBank : Set₁ where     -- was : Set₂
  field
    primes        : Word ℕ
    Reference     : ℕ → Set
    VCOState      : ℕ → Set
    pll-at        : (p : ℕ) → PLL (Reference p) (VCOState p)
    lock-state-at : ℕ → LockState

open PLLBank public
