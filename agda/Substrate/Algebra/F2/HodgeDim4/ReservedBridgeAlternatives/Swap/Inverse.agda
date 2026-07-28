------------------------------------------------------------------------
-- Substrate.Algebra.F2.HodgeDim4.ReservedBridgeAlternatives.Swap.Inverse
--
-- Inverse extraction matching the swap permuted assignment:
--   extract c₀ from lookup 0, c₁ from lookup 2, c₂ from lookup 1.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.F2.HodgeDim4.ReservedBridgeAlternatives.Swap.Inverse where

open import Substrate.Foundation.Fin.Fin
open import Substrate.Foundation.Fin.Literals using (₀; ₁; ₂)
open import Substrate.Foundation.Vec using ([]; _∷_; lookup)
open import Substrate.Algebra.F2.Vector using (Vector)
open import Substrate.Algebra.F2.HodgeDim4.Bivector using (Bivector)

selfdual-coefficients-swap : Bivector → Vector 3
selfdual-coefficients-swap ω =
  lookup ω zero ∷ lookup ω ₂ ∷ lookup ω ₁ ∷ []
