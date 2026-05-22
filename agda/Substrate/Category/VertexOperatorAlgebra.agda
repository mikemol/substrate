------------------------------------------------------------------------
-- Substrate.Category.VertexOperatorAlgebra
--
-- R8 of the R-arc. Vertex Operator Algebra primitive (Borcherds 1986).
-- Graded vector space V = ⊕_n V_n + vacuum 𝟙 + conformal vector ω +
-- vertex operator Y(_, z) : V → End(V)[[z, z⁻¹]] satisfying VOA
-- axioms (locality, weight grading, …).
--
-- Per [[categorical-name-first]]: VOA is the standard structural
-- name; foundation for R9 MonsterVOA (V♮).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Category.VertexOperatorAlgebra where

open import Level using (Level; _⊔_) renaming (suc to lsuc)
open import Substrate.Foundation.Nat using (ℕ)

record VertexOperatorAlgebra : Set₁ where
  field
    V         : ℕ → Set       -- graded carrier V = ⊕_n V_n
    vacuum    : V 0           -- 𝟙 (vacuum vector in weight 0)
    conformal : V 2           -- ω (conformal vector in weight 2)
  -- Vertex operator Y(_, z), locality, weight-grading, Borcherds
  -- identity: user obligations per substrate-pragmatic minimum.
