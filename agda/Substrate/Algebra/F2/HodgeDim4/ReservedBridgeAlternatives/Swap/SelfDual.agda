------------------------------------------------------------------------
-- Substrate.Algebra.F2.HodgeDim4.ReservedBridgeAlternatives.Swap.SelfDual
--
-- Swap alternative is closed in SelfDual.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.F2.HodgeDim4.ReservedBridgeAlternatives.Swap.SelfDual where

open import Substrate.Foundation.Vec using ([]; _∷_)
open import Substrate.Algebra.F2.Vector using (Vector; _+ⱽ_; _*ₛ_)
open import Substrate.Algebra.F2.HodgeDim4.SelfDual
  using ( SelfDual-Pred
        ; sd-pair-01-23; sd-pair-02-13; sd-pair-03-12
        ; sd-pair-01-23-self-dual
        ; sd-pair-02-13-self-dual
        ; sd-pair-03-12-self-dual
        ; sd-closed-+ⱽ; sd-closed-*ₛ
        )
open import Substrate.Algebra.F2.HodgeDim4.ReservedBridgeAlternatives.Swap.Forward
  using (vector3-to-selfdual-swap)

vector3-to-selfdual-swap-sd :
  (v : Vector 3) → SelfDual-Pred (vector3-to-selfdual-swap v)
vector3-to-selfdual-swap-sd (c₀ ∷ c₁ ∷ c₂ ∷ []) =
  sd-closed-+ⱽ
    (c₀ *ₛ sd-pair-01-23)
    ((c₁ *ₛ sd-pair-03-12) +ⱽ (c₂ *ₛ sd-pair-02-13))
    (sd-closed-*ₛ c₀ sd-pair-01-23 sd-pair-01-23-self-dual)
    (sd-closed-+ⱽ
      (c₁ *ₛ sd-pair-03-12)
      (c₂ *ₛ sd-pair-02-13)
      (sd-closed-*ₛ c₁ sd-pair-03-12 sd-pair-03-12-self-dual)
      (sd-closed-*ₛ c₂ sd-pair-02-13 sd-pair-02-13-self-dual))
