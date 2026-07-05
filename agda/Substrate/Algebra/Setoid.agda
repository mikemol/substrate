------------------------------------------------------------------------
-- Substrate.Algebra.Setoid
--
-- Set1 of the Setoid sibling tower per [scratch/m_mod_arc_plan.md]
-- (sibling-towers section).
--
-- A Setoid bundles a carrier with an equivalence relation. This is
-- the substrate-native variant of stdlib's `Relation.Binary.Setoid`,
-- avoiding the level-polymorphic machinery in favour of a single
-- propositional-equality-tracking record.
--
-- Substrate-native scope: per [[feedback-minimize-stdlib-deps]] we
-- avoid stdlib's heavy Relation.Binary infrastructure. The Setoid
-- record here uses a relation `_≈_` and three witnesses (reflexive,
-- symmetric, transitive). The intended use is to give a coarser
-- equivalence than `_≡_` for downstream language-categorical work
-- (LanguageMorphism quotients at the Yoneda side).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.Setoid where

open import Substrate.Foundation.Eq using (_≡_; refl; sym; trans)

------------------------------------------------------------------------
-- 1. The Setoid record.
--
-- Parametric in a carrier A and a relation _≈_ : A → A → Set.
-- Three witnesses package the equivalence laws.
------------------------------------------------------------------------

record Setoid (A : Set) : Set₁ where      -- ⟦shape:883de482 _≈_,≈-refl,≈-sym⟧
  field
    _≈_ : A → A → Set
    ≈-refl  : (a : A) → a ≈ a
    ≈-sym   : {a b : A} → a ≈ b → b ≈ a
    ≈-trans : {a b c : A} → a ≈ b → b ≈ c → a ≈ c

open Setoid public

------------------------------------------------------------------------
-- 2. The propositional Setoid: _≡_ is the finest equivalence.
--
-- The canonical Setoid on any A with the equivalence being _≡_.
------------------------------------------------------------------------

≡-Setoid : (A : Set) → Setoid A
≡-Setoid A = record
  { _≈_     = _≡_
  ; ≈-refl  = λ _ → refl
  ; ≈-sym   = sym
  ; ≈-trans = trans
  }

------------------------------------------------------------------------
-- 3. Capstone for Set1.
--
-- Setoid record landed. Set2 supplies SetoidMap (structure-
-- preserving function up to equivalence); Set3 the LanguageMorphism-
-- specific Setoid; Set4-Set5 close the Yoneda respect-≈M gap.
------------------------------------------------------------------------
