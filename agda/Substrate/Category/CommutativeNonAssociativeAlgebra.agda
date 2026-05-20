------------------------------------------------------------------------
-- Substrate.Category.CommutativeNonAssociativeAlgebra
--
-- The categorical primitive for commutative non-associative algebras
-- with a symmetric bilinear form satisfying form-product associativity:
--   ⟨xy, z⟩ = ⟨x, yz⟩
-- (the "Frobenius condition" for the form).
--
-- X3 of the 20-slice arc per [[prime-factored-gauge-arc]] follow-on.
-- Foundational for X4 (GriessAlgebra primitive) and X5
-- (Monster.AsGriessAlgebra).
--
-- The Griess algebra (Griess 1982; later identified as the weight-2
-- piece of Frenkel-Lepowsky-Meurman's V♮) is a 196,884-dim
-- commutative non-associative algebra over ℝ whose automorphism
-- group is the Monster. This primitive captures the abstract
-- algebraic structure; X4 specialises to the Griess shape (specific
-- dimension + structure constants parametric).
--
-- Per [[categorical-name-first]]: "commutative non-associative
-- algebra with invariant form" / "commutative power-associative
-- algebra" / "Vinberg cone algebra" are standard categorical names
-- depending on which additional axioms one imposes. The substrate
-- primitive takes the minimal-axiom version: commutativity + form +
-- form-product associativity. Specialisations (e.g., adding a unit
-- via Frobenius-form-with-counit) layer on top.
--
-- Per [[continuous-via-discrete-inference-rules]]: the carrier is
-- abstract (user-supplied Set); the algebra structure is the
-- substrate's content. Specific 196,884-dim instance is X4.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Category.CommutativeNonAssociativeAlgebra where

open import Level using (Level; _⊔_) renaming (suc to lsuc)
open import Relation.Binary.PropositionalEquality using (_≡_)

private
  variable
    ℓ ℓV : Level

------------------------------------------------------------------------
-- The CommutativeNonAssociativeAlgebra record.
--
-- Bundles:
--   * V : Set — carrier (typically a finite-dim vector space)
--   * Scalar : Set — the scalar field for the form (typically ℝ or ℚ)
--   * 0V : V — zero vector
--   * _+V_ : V → V → V — vector addition
--   * _·_ : V → V → V — the algebra product (commutative, possibly
--     non-associative)
--   * ⟨_,_⟩ : V → V → Scalar — symmetric bilinear form
--   * comm : commutativity of _·_
--   * sym : symmetry of ⟨_,_⟩
--   * form-product-assoc : ⟨ xy , z ⟩ ≡ ⟨ x , yz ⟩ ("Frobenius
--     condition" — the invariance of the form under multiplication
--     by elements; equivalent to the form being an algebra-
--     homomorphism into Scalar in the appropriate categorical sense)
--
-- Per substrate convention: minimum-axiom record. Additional
-- structure (associativity, unital, etc.) layered as specialised
-- records.
------------------------------------------------------------------------

record CommutativeNonAssociativeAlgebra : Set (lsuc (ℓ ⊔ ℓV)) where
  constructor mkCNAA
  field
    V               : Set ℓ
    Scalar          : Set ℓV
    0V              : V
    _+V_            : V → V → V
    _·_             : V → V → V
    ⟨_,_⟩           : V → V → Scalar
    comm            : (x y : V) → (x · y) ≡ (y · x)
    sym-form        : (x y : V) → ⟨ x , y ⟩ ≡ ⟨ y , x ⟩
    form-prod-assoc : (x y z : V) → ⟨ (x · y) , z ⟩ ≡ ⟨ x , (y · z) ⟩

------------------------------------------------------------------------
-- Capstone — algebra primitive in place.
--
-- X3 of the 20-slice arc. Foundation for X4 (GriessAlgebra) + X5
-- (Monster.AsGriessAlgebra).
--
-- Concrete instances expected:
--   * Griess algebra (X4): V = 196,884-dim ℝ-vector space; product +
--     form from the algebra construction (Griess 1982).
--   * V♮ weight-2 piece (FLM 1988): same as Griess via FLM's
--     identification.
--   * Smaller non-associative algebras (Cayley/octonion-like,
--     Jordan-algebra fragments, etc.) following the same template.
--
-- Per [[categorical-name-first]]: standard naming. Per
-- [[expose-generator-not-orbit]]: the algebra structure (= V's
-- dimension + structure constants) IS the generator; the
-- automorphism group is the orbit.
--
-- Next: X4 (GriessAlgebra parametric).
------------------------------------------------------------------------
