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

open import Substrate.Foundation.Level using (Level)
open import Substrate.Foundation.Nat using (ℕ)

open import Substrate.Category.VertexOperatorAlgebra
  using (VertexOperatorAlgebra)

-- ⟡set1-paydown: VertexOperatorAlgebra now parameterizes its graded carrier family
-- V : ℕ → Set, so this module threads V as a param too.
module Substrate.Algebra.Sporadic.MonsterVOA
  (V : ℕ → Set)
  (V♮ : VertexOperatorAlgebra V)
  where

MonsterVOA-V♮ : VertexOperatorAlgebra V
MonsterVOA-V♮ = V♮
