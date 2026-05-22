------------------------------------------------------------------------
-- Substrate.Algebra.F2.HodgeDim4.ReservedBridgeAlternatives.Swap.Forward
--
-- Last-two-transposition forward map:
--   (c₀, c₁, c₂) ↦ c₀ *ₛ sd-pair-01-23 + c₁ *ₛ sd-pair-03-12 + c₂ *ₛ sd-pair-02-13.
-- Swaps the targets of c₁ and c₂ relative to the canonical bridge.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.F2.HodgeDim4.ReservedBridgeAlternatives.Swap.Forward where

open import Substrate.Foundation.Vec using ([]; _∷_)
open import Substrate.Algebra.F2.Vector using (Vector; _+ⱽ_; _*ₛ_)
open import Substrate.Algebra.F2.HodgeDim4.Bivector using (Bivector)
open import Substrate.Algebra.F2.HodgeDim4.SelfDual
  using (sd-pair-01-23; sd-pair-02-13; sd-pair-03-12)

vector3-to-selfdual-swap : Vector 3 → Bivector
vector3-to-selfdual-swap (c₀ ∷ c₁ ∷ c₂ ∷ []) =
  (c₀ *ₛ sd-pair-01-23) +ⱽ
  ((c₁ *ₛ sd-pair-03-12) +ⱽ (c₂ *ₛ sd-pair-02-13))
