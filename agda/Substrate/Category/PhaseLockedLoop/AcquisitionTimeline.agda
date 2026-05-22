------------------------------------------------------------------------
-- Substrate.Category.PhaseLockedLoop.AcquisitionTimeline
--
-- Substrate-aligned acquisition timeline: for Sylow primes
-- {2, 3, 5, 7, 11, 13} with 3-cycle activation, the bank's
-- lock-state trajectory is fully determined by chain position.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Category.PhaseLockedLoop.AcquisitionTimeline where

open import Substrate.Foundation.Nat using (ℕ)
open import Substrate.Foundation.Eq using (_≡_; refl)

record AcquisitionTimeline : Set where
  field
    activate-at-2  : ℕ
    activate-at-3  : ℕ
    activate-at-5  : ℕ
    activate-at-7  : ℕ
    activate-at-11 : ℕ
    activate-at-13 : ℕ

    rule-2  : activate-at-2  ≡ 6
    rule-3  : activate-at-3  ≡ 9
    rule-5  : activate-at-5  ≡ 15
    rule-7  : activate-at-7  ≡ 21
    rule-11 : activate-at-11 ≡ 33
    rule-13 : activate-at-13 ≡ 39

open AcquisitionTimeline public

substrate-3cycle-timeline : AcquisitionTimeline
substrate-3cycle-timeline = record
  { activate-at-2  = 6
  ; activate-at-3  = 9
  ; activate-at-5  = 15
  ; activate-at-7  = 21
  ; activate-at-11 = 33
  ; activate-at-13 = 39
  ; rule-2  = refl
  ; rule-3  = refl
  ; rule-5  = refl
  ; rule-7  = refl
  ; rule-11 = refl
  ; rule-13 = refl
  }
