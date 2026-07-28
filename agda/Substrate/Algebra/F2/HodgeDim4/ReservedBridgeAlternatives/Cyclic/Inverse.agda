------------------------------------------------------------------------
-- Substrate.Algebra.F2.HodgeDim4.ReservedBridgeAlternatives.Cyclic.Inverse
--
-- Inverse extraction matching the cyclic permuted assignment:
--   extract c₀ from lookup 1, c₁ from lookup 2, c₂ from lookup 0.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.F2.HodgeDim4.ReservedBridgeAlternatives.Cyclic.Inverse where

open import Substrate.Foundation.Fin.Fin
open import Substrate.Foundation.Fin.Literals using (₀; ₁; ₂)
open import Substrate.Foundation.Vec using ([]; _∷_; lookup)
open import Substrate.Algebra.F2.Vector using (Vector)
open import Substrate.Algebra.F2.HodgeDim4.Bivector using (Bivector)

selfdual-coefficients-cyclic : Bivector → Vector 3
selfdual-coefficients-cyclic ω =
  lookup ω ₁ ∷ lookup ω ₂ ∷ lookup ω zero ∷ []
