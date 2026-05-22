------------------------------------------------------------------------
-- Substrate.Category.RuleAction.ComposeAffine
--
-- compose-affine : the AffineProjection composition law. start-phase
-- adds; length-mask picks the first non-nothing value.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Category.RuleAction.ComposeAffine where

open import Substrate.Foundation.Nat using (ℕ; _+_)
open import Substrate.Foundation.Maybe using (Maybe; just; nothing)
open import Substrate.Category.RuleAction.AffineProjection
  using (AffineProjection; start-phase; length-mask)

compose-affine : AffineProjection → AffineProjection → AffineProjection
compose-affine a₁ a₂ = record
  { start-phase = start-phase a₁ + start-phase a₂
  ; length-mask = pick-length (length-mask a₁) (length-mask a₂)
  }
  where
    pick-length : Maybe ℕ → Maybe ℕ → Maybe ℕ
    pick-length (just l) _ = just l
    pick-length nothing  m = m
