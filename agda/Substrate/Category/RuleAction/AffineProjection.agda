------------------------------------------------------------------------
-- Substrate.Category.RuleAction.AffineProjection
--
-- Affine-projection factor of A: (start_phase, length_mask).
-- Subsumes LZ77 backref offsets. Includes the identity affine.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Category.RuleAction.AffineProjection where

open import Substrate.Foundation.Nat using (ℕ; zero)
open import Substrate.Foundation.Maybe using (Maybe; nothing)

record AffineProjection : Set where
  field
    start-phase : ℕ
    length-mask : Maybe ℕ    -- nothing = "use full suffix"

open AffineProjection public

identity-affine : AffineProjection
identity-affine = record { start-phase = 0 ; length-mask = nothing }
