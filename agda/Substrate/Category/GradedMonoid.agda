------------------------------------------------------------------------
-- Substrate.Category.GradedMonoid
--
-- Primitive #8 in the Substrate.Category.Primitives roadmap.
-- ℕ-graded monoid: a monoid M with a degree function to ℕ that's a
-- monoid homomorphism.
--
-- Formally: GradedMonoid = Monoid + (degree : M → ℕ) such that
--   * degree ε ≡ 0
--   * degree (a · b) ≡ degree a + degree b
--
-- The grading function turns M into a monoid HOM to (ℕ, +, 0).
-- Equivalent to a monoid homomorphism M → ℕ; this record packages
-- the data.
--
-- Per [[project-graded-bicategorical-arc]]: this is the substrate's
-- formal handle on "degree." FreeCyclic-Coxeter (with length as the
-- degree) is the canonical instance.
--
-- Per [[feedback-categorical-name-first]]: "ℕ-graded monoid" is the
-- standard name. The substrate has been using length implicitly;
-- this primitive surfaces it.
--
-- Scope: ℕ-grading specifically. General R-graded monoids (with R
-- any commutative monoid) is a follow-on if a use site demands.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Category.GradedMonoid where

open import Substrate.Foundation.Nat using (ℕ; zero; suc; _+_)
open import Substrate.Foundation.Level using (Level; _⊔_) renaming (suc to lsuc)
open import Substrate.Foundation.Eq using (_≡_; refl)

private
  variable
    ℓ : Level

------------------------------------------------------------------------
-- The GradedMonoid record.
------------------------------------------------------------------------

-- ⟡set1-rp-gradedmonoid: the carrier M is a PARAMETER now (set1-carrier-always-parameterize);
-- the record drops Set (lsuc ℓ) → Set ℓ.
record GradedMonoid {ℓ : Level} (M : Set ℓ) : Set ℓ where
  field
    -- Monoid composition.
    _·_ : M → M → M
    -- Monoid identity.
    ε : M
    -- Monoid laws.
    ·-assoc      : (a b c : M) → (a · b) · c ≡ a · (b · c)
    ·-identityˡ  : (a : M) → ε · a ≡ a
    ·-identityʳ  : (a : M) → a · ε ≡ a
    -- Degree function (= ℕ-grading).
    degree       : M → ℕ
    degree-ε     : degree ε ≡ 0
    degree-·     : (a b : M) → degree (a · b) ≡ degree a + degree b

------------------------------------------------------------------------
-- Capstone.
--
-- After this slice: any monoid with a length-or-size function that
-- respects identity and composition gives a GradedMonoid instance.
-- Slice 5 instantiates with FreeCyclic-Coxeter (length is the
-- canonical grading).
--
-- The "degree" is a structural concept across the substrate:
--   * Word length in any Coxeter group (subject to normalization).
--   * Cycle count in the 2-D word algebra (FreeCyclic component).
--   * Polynomial degree (= leading index) in Polynomial algebra.
--   * Vector "support size" / "weight" (number of nonzero entries)
--     in F₂-vector codes.
-- Each is a potential GradedMonoid instance via the degree
-- homomorphism property.
--
-- Per [[project-graded-bicategorical-arc]]: the GradedMonoid record
-- is the primitive that opens the categorical "enrichment-over-ℕ"
-- reading — the structure that makes the substrate's word algebra
-- a graded bicategory rather than just a 2-monoid.
--
-- Deferred follow-ons:
--
--   * **General R-graded monoid**: replace ℕ with any commutative
--     monoid R. The substrate has Z₂ (parity grading), Z (signed
--     grading), etc., as natural R candidates.
--
--   * **Graded modules over GradedMonoid**: linear-algebra-style
--     module structure where the module's grading respects the
--     ring's grading. Used for graded ring theory.
------------------------------------------------------------------------
