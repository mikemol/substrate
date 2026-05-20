------------------------------------------------------------------------
-- Substrate.Category.JordanAlgebra
--
-- The categorical primitive for Jordan algebras.
--
-- A Jordan algebra is a commutative (possibly non-associative) algebra
-- satisfying the Jordan identity
--   (x² · y) · x ≡ x² · (y · x)
-- where x² = x · x. The Jordan identity weakens associativity to a
-- specific exchange rule involving squares.
--
-- L16 of the L-arc. Foundational structural sibling of X3
-- [[CommutativeNonAssociativeAlgebra]] (CNAA): CNAA + Jordan identity
-- = JordanAlgebra. Jordan algebras are intermediate between
-- commutative associative algebras (= associative-as-Jordan, the
-- trivial case) and the wider class of commutative non-associative
-- algebras (= CNAA, which Griess inhabits but Jordan does not).
--
-- Per [[categorical-name-first]]: "Jordan algebra" is the standard
-- categorical name (Jordan 1933; Albert 1947 for the classification).
-- Universal-property characterisations:
--   * Special Jordan algebras: x ∘ y = ½(xy + yx) in an associative
--     algebra (need 2 invertible)
--   * Exceptional: the Albert algebra (27-dim, only exception to the
--     classification by Albert; closely related to E₈, the Octonions,
--     and the Magic Square)
--
-- Per [[continuous-via-discrete-inference-rules]]: the carrier is
-- abstract (user-supplied); the substrate captures the Jordan
-- structure as a record bundling commutative · + Jordan identity.
--
-- Specific instances (L-arc + beyond):
--   * L17 GriessAlgebra.AsJordan (PARAMETRIC; only constructible if
--     the user can supply the Jordan identity for Griess — see L17's
--     header for the caveat)
--   * Spin factors JSpin_n = ℝ ⊕ ℝⁿ with (a, v) · (b, w) =
--     (ab + ⟨v,w⟩, aw + bv) (deferred; not in L-arc scope)
--   * Hermitian matrices over ℝ / ℂ / ℍ under symmetric product
--     (deferred)
--   * Albert algebra (exceptional 27-dim Jordan; deferred —
--     connected to E₈)
--
-- Per the substrate's [[expose-generator-not-orbit]]: the basis +
-- structure constants are the generator; the orbit (Jordan
-- automorphism group) is downstream.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Category.JordanAlgebra where

open import Level using (Level; _⊔_) renaming (suc to lsuc)
open import Relation.Binary.PropositionalEquality using (_≡_)

private
  variable
    ℓ : Level

------------------------------------------------------------------------
-- The JordanAlgebra record.
--
-- Bundles:
--   * V : Set — carrier
--   * 0V : V, _+V_ — additive structure
--   * _·_ : V → V → V — the Jordan product (commutative)
--   * comm : (x y : V) → (x · y) ≡ (y · x)
--   * jordan : (x y : V) → ((x · x) · y) · x ≡ (x · x) · (y · x)
--
-- The Jordan identity is the only non-trivial axiom; everything
-- else is bilinear-algebra-baseline.
------------------------------------------------------------------------

record JordanAlgebra : Set (lsuc ℓ) where
  constructor mkJordanAlgebra
  field
    V       : Set ℓ
    0V      : V
    _+V_    : V → V → V
    _·_     : V → V → V
    comm    : (x y : V) → (x · y) ≡ (y · x)
    jordan  : (x y : V) →
              (((x · x) · y) · x) ≡ ((x · x) · (y · x))

------------------------------------------------------------------------
-- Capstone — Jordan algebra primitive in place.
--
-- L16 of the L-arc. Opens phase Λ''' (L16-L20):
--   L16 JordanAlgebra (this)
--   L17 GriessAlgebra.AsJordan (parametric bridge, no overclaim)
--   L18 UniversalEnvelopingAlgebra (Lie → Assoc adjunction)
--   L19 MonsterLieAlgebra (Borcherds 1992)
--   L20 capstone refresh
--
-- Per the substrate's algebra-primitive taxonomy after L16:
--   * Anti-commutative: L1 ACA + L2 LieAlgebra (Lie)
--   * Commutative non-associative (no form): L16 JordanAlgebra (this)
--   * Commutative non-associative with form: X3 CNAA + X4 Griess
--   * Graded multilinear: L3 ExteriorAlgebra + L4 WedgeProduct
--
-- The substrate now spans the standard algebraic-structure taxonomy
-- relevant to the Monster + Lie + Coxeter recursion.
--
-- Next: L17 GriessAlgebra.AsJordan (parametric).
------------------------------------------------------------------------
