------------------------------------------------------------------------
-- Substrate.Category.CommutativeMonoid
--
-- The commutative monoid record. Foundational for the R-graded
-- GradedMonoid (slice 12) where R is the grading commutative monoid.
--
-- A commutative monoid is a monoid (M, ·, ε) with commutativity:
--   a · b ≡ b · a.
--
-- Standard categorical concept; the substrate has been using ℕ and
-- F₂ as commutative monoids implicitly. This primitive surfaces the
-- abstraction.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Category.CommutativeMonoid where

open import Level using (Level) renaming (suc to lsuc)
open import Relation.Binary.PropositionalEquality using (_≡_)

private
  variable
    ℓ : Level

------------------------------------------------------------------------
-- The CommutativeMonoid record.
------------------------------------------------------------------------

record CommutativeMonoid (ℓ : Level) : Set (lsuc ℓ) where
  field
    R           : Set ℓ
    _+R_        : R → R → R
    0R          : R
    +R-assoc        : (a b c : R) → (a +R b) +R c ≡ a +R (b +R c)
    +R-identityˡ    : (a : R) → 0R +R a ≡ a
    +R-identityʳ    : (a : R) → a +R 0R ≡ a
    +R-comm         : (a b : R) → a +R b ≡ b +R a

------------------------------------------------------------------------
-- Capstone.
--
-- ℕ is the canonical CommutativeMonoid (+, 0); F₂ is the canonical
-- finite CommutativeMonoid (+_F₂, 𝟘). Slices 13 and following
-- instantiate.
--
-- The R-graded GradedMonoid (slice 12) is parameterized by a
-- CommutativeMonoid R; ℕ-graded GradedMonoid (the version in
-- Substrate.Category.GradedMonoid) is the R = ℕ case.
------------------------------------------------------------------------
