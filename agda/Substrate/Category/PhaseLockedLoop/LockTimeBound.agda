------------------------------------------------------------------------
-- Substrate.Category.PhaseLockedLoop.LockTimeBound
--
-- Lock-time bound: lock time ∝ prime.
--   lock-time(p) ≥ k · p  (k typically 3-5)
--   lock-time(p) ≤ K · p  (K bounded for stationary corpora)
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Category.PhaseLockedLoop.LockTimeBound where

open import Substrate.Foundation.Nat using (ℕ; _*_)

record LockTimeBound : Set where
  field
    prime           : ℕ
    min-cycles      : ℕ
    max-cycles      : ℕ
    lower-bound-pos : ℕ
    upper-bound-pos : ℕ

open LockTimeBound public

mkLockBound : (p k K : ℕ) → LockTimeBound
mkLockBound p k K = record
  { prime = p
  ; min-cycles = k
  ; max-cycles = K
  ; lower-bound-pos = k * p
  ; upper-bound-pos = K * p
  }
