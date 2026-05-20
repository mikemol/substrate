------------------------------------------------------------------------
-- Substrate.Algebra.Sporadic.MonsterVOA
--
-- R9 of the R-arc. The Moonshine module V♮ (Frenkel-Lepowsky-Meurman
-- 1988) as a substrate VertexOperatorAlgebra instance.
--
-- V♮ is the canonical VOA whose Aut = Monster; its weight-2 piece IS
-- the Griess algebra (per X4). Module-parametric: user supplies V♮
-- as a VOA via R8.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

open import Level using (Level)

open import Substrate.Category.VertexOperatorAlgebra
  using (VertexOperatorAlgebra)

module Substrate.Algebra.Sporadic.MonsterVOA
  (V♮ : VertexOperatorAlgebra)
  where

MonsterVOA-V♮ : VertexOperatorAlgebra
MonsterVOA-V♮ = V♮
