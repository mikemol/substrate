------------------------------------------------------------------------
-- Substrate.Category.Strict2Monoid
--
-- Primitive #7 in the Substrate.Category.Primitives roadmap.
-- The 1-object strict 2-category, packaged as a record.
--
-- A 1-object strict 2-category (= "strict 2-monoid") has:
--   * 0-cells: a single object (trivial; implicit).
--   * 1-cells: an underlying type M (= the homset of the 1 object).
--   * Horizontal composition: _·_ : M → M → M, strict associative.
--   * Identity 1-cell: ε : M.
--   * 2-cells: _≈_ : M → M → Set.
--   * Vertical composition: ≈ is reflexive, symmetric, transitive.
--   * Horizontal composition of 2-cells: ·-cong respects ≈
--     componentwise.
--
-- Per `feedback_categorical_name_first`: this is the standard
-- categorical structure that the substrate's Coxeter Core
-- IMPLICITLY carries. The Word/_++_/_≈_ trio of Coxeter Core IS a
-- Strict2Monoid; this record names it.
--
-- Per [[project-graded-bicategorical-arc]]: this primitive opens
-- the graded-bicategorical arc by giving an abstract handle on the
-- structure that Coxeter + FreeCyclic + DirectProduct implicitly
-- carry.
--
-- Scope discipline: STRICT case only. Weak (bicategory) requires
-- coherence cells (pentagon, triangle iso); the substrate's _·_
-- (= normalize ∘ ++) is weak (associative up to ≈, not on the
-- nose), but ++ is strict — this primitive captures the ++ flavor.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Category.Strict2Monoid where

open import Substrate.Foundation.Level using (Level; _⊔_; suc)
open import Substrate.Foundation.Eq using (_≡_)

private
  variable
    ℓ ℓ′ : Level

------------------------------------------------------------------------
-- The Strict2Monoid record.
------------------------------------------------------------------------

record Strict2Monoid (ℓ ℓ′ : Level) : Set (suc (ℓ ⊔ ℓ′)) where
  field
    -- 1-cell type (the underlying monoid carrier).
    M       : Set ℓ
    -- Horizontal composition (1-cell composition).
    _·_     : M → M → M
    -- Identity 1-cell.
    ε       : M
    -- Monoid laws — STRICT (propositional ≡).
    ·-assoc      : (a b c : M) → (a · b) · c ≡ a · (b · c)
    ·-identityˡ  : (a : M) → ε · a ≡ a
    ·-identityʳ  : (a : M) → a · ε ≡ a
    -- 2-cell relation.
    _≈_     : M → M → Set ℓ′
    -- Vertical composition (2-cell composition).
    ≈-refl  : ∀ {a} → a ≈ a
    ≈-sym   : ∀ {a b} → a ≈ b → b ≈ a
    ≈-trans : ∀ {a b c} → a ≈ b → b ≈ c → a ≈ c
    -- Horizontal composition of 2-cells.
    ·-cong  : ∀ {a a' b b'} → a ≈ a' → b ≈ b' → (a · b) ≈ (a' · b')

------------------------------------------------------------------------
-- Capstone — Strict2Monoid primitive introduced.
--
-- After this slice, any structure with (M, _·_, ε, ≈) satisfying
-- the monoid laws + the 2-cell laws gives a Strict2Monoid instance.
-- The substrate's Coxeter Core's Word/_++_/_≈_ trio is the canonical
-- instance (slice 2).
--
-- Substrate-wide implication: each Coxeter group (Z₂, Z₃, Z₄, Z₅,
-- V₄, FreeCyclic, DirectProduct combinations) inherits Strict2Monoid
-- structure via the constructor in slice 2.
--
-- Per [[feedback-categorical-name-first]]: "1-object strict 2-category"
-- is the established name. The substrate's word + normalize trio
-- IS this structure; naming it explicitly opens the categorical
-- toolkit (functors between Strict2Monoids, 2-natural transformations,
-- adjunctions, etc.).
--
-- Deferred follow-ons:
--
--   * **Weak 2-monoid (Bicategory)**: when associativity holds only
--     up to ≈ (not on the nose). The substrate's _·_ (= normalize
--     ∘ ++) is this flavor; modelling requires coherence cells.
--
--   * **Functor Strict2Monoid → Strict2Monoid**: monoid morphism
--     respecting both 1-cell composition and 2-cells. Phase-projection
--     from slice 4 of the previous arc IS such a functor.
--
--   * **Strict n-monoid**: nested DirectProduct of Strict2Monoids gives
--     n-fold composition axes. Slice 7 of this arc instantiates.
------------------------------------------------------------------------
