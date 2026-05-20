------------------------------------------------------------------------
-- Substrate.Algebra.Sporadic.GriessAlgebra
--
-- The Griess algebra as a parametric CommutativeNonAssociativeAlgebra
-- instance. 196,884-dimensional commutative non-associative algebra
-- over ℝ (or ℚ with rational structure constants) whose automorphism
-- group preserving the form is the Monster.
--
-- X4 of the 20-slice arc per [[prime-factored-gauge-arc]] follow-on.
-- Foundation for X5 (Monster.AsGriessAlgebra) — the identification
-- M ≅ Aut(GriessAlgebra) closing the Q4 strand of [[q1-q5-entailment-
-- chain]].
--
-- History: constructed by Griess (1982) directly as a commutative
-- non-associative algebra with explicit structure constants; later
-- identified by Frenkel-Lepowsky-Meurman (1988) as the weight-2
-- piece of the Moonshine vertex operator algebra V♮ = Aut⁻¹(M).
--
-- Per [[continuous-via-discrete-inference-rules]]: the 196,884-dim
-- carrier is abstract (user supplies as a Set); the algebra structure
-- (commutativity, form symmetry, form-product associativity) is
-- packaged via the X3 CommutativeNonAssociativeAlgebra primitive.
--
-- Per Q5 of [[q1-q5-entailment-chain]]: the 196,884² ≈ 4×10^10
-- structure constants reduce to ~50 orbit representatives via
-- M-equivariance — the substrate-friendly reduction. This module
-- takes the structure constants as input parameters; orbit-reduction
-- inference is a downstream slice.
--
-- Module-parametric over (V, scalars, ops, axioms) supplied by the
-- user. The substrate's role is to BRIDGE Griess's external
-- construction into the substrate's CNAA primitive.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

open import Level using (Level)
open import Relation.Binary.PropositionalEquality using (_≡_)

open import Substrate.Category.CommutativeNonAssociativeAlgebra
  using (CommutativeNonAssociativeAlgebra; mkCNAA)

module Substrate.Algebra.Sporadic.GriessAlgebra
  -- Carrier: abstract 196,884-dim vector space over Scalar.
  {ℓ ℓV : Level}
  (V : Set ℓ)
  (Scalar : Set ℓV)
  -- Algebra structure.
  (0V : V)
  (_+V_ : V → V → V)
  (_·_ : V → V → V)
  (⟨_,_⟩ : V → V → Scalar)
  -- Axioms.
  (comm : (x y : V) → (x · y) ≡ (y · x))
  (sym-form : (x y : V) → ⟨ x , y ⟩ ≡ ⟨ y , x ⟩)
  (form-prod-assoc : (x y z : V) → ⟨ (x · y) , z ⟩ ≡ ⟨ x , (y · z) ⟩)
  where

------------------------------------------------------------------------
-- 1. The Griess algebra as a CommutativeNonAssociativeAlgebra.
------------------------------------------------------------------------

GriessAlgebra : CommutativeNonAssociativeAlgebra
GriessAlgebra = mkCNAA
  V Scalar 0V _+V_ _·_ ⟨_,_⟩
  comm sym-form form-prod-assoc

------------------------------------------------------------------------
-- 2. Documented dimension (= 196,884; ATLAS / Griess 1982 / FLM 1988).
------------------------------------------------------------------------

open import Data.Nat using (ℕ)

GriessAlgebra-dimension : ℕ
GriessAlgebra-dimension = 196884

------------------------------------------------------------------------
-- 3. Capstone — Griess algebra as substrate primitive instance.
--
-- X4 of the 20-slice arc. With X4 landed, the substrate has the
-- structural target M = Aut(GriessAlgebra) accessible via the X3
-- primitive interface.
--
-- Module-parametric over the 196,884-dim carrier + product + form +
-- axioms. Concrete data (specific structure constants) supplied by
-- downstream consumers citing Griess 1982 / FLM 1988 / ATLAS.
--
-- Per Q5 of [[q1-q5-entailment-chain]]: structure-constant reduction
-- via M-equivariance is a follow-on slice (substrate's word-algebra
-- inference at the algebra level).
--
-- Next: X5 (Monster.AsGriessAlgebra identification + master capstone
-- closing all 4 sub-arcs).
------------------------------------------------------------------------
