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

open import Substrate.Foundation.Level using (Level; _⊔_) renaming (suc to lsuc)
open import Substrate.Foundation.Nat using (ℕ)

-- ⟡set1-paydown: parameterize the graded carrier family V : ℕ → Set out of the
-- record (substrate stance: families are module params, never fields). The record
-- drops from Set₁ to Set; consumers write `VertexOperatorAlgebra V`.
module _ (V : ℕ → Set) where       -- V = ⊕_n V_n, the graded carrier family
  record VertexOperatorAlgebra : Set where
    field
      vacuum    : V 0           -- 𝟙 (vacuum vector in weight 0)
      conformal : V 2           -- ω (conformal vector in weight 2)
  -- Vertex operator Y(_, z), locality, weight-grading, Borcherds
  -- identity: user obligations per substrate-pragmatic minimum.
