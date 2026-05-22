------------------------------------------------------------------------
-- Substrate.Algebra.Setoid.Map
--
-- Set2 of the Setoid sibling tower per [scratch/m_mod_arc_plan.md].
--
-- A SetoidMap is a function between Setoids that respects the
-- equivalence relation: a ≈ b ⟹ f a ≈ f b. This is the standard
-- "morphism in the category of Setoids" data.
--
-- The substrate's B-arc IsNatural respect-≈M gap is closed by
-- noting that any naturality witness IS a SetoidMap between
-- LanguageMorphism Setoids (Set3).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.Setoid.Map where

open import Substrate.Algebra.Setoid using (Setoid; _≈_)

------------------------------------------------------------------------
-- 1. The SetoidMap record.
--
-- Bundles a function f : A → B with the witness that f respects the
-- equivalence relations on A and B.
------------------------------------------------------------------------

record SetoidMap
  {A B : Set}
  (S-A : Setoid A) (S-B : Setoid B)
  : Set where
  field
    apply : A → B
    respect-≈ :
      {a b : A} → _≈_ S-A a b → _≈_ S-B (apply a) (apply b)

open SetoidMap public

------------------------------------------------------------------------
-- 2. Identity SetoidMap and composition.
------------------------------------------------------------------------

id-SetoidMap :
  {A : Set} (S-A : Setoid A) → SetoidMap S-A S-A
id-SetoidMap S-A = record
  { apply     = λ a → a
  ; respect-≈ = λ p → p
  }

compose-SetoidMap :
  {A B C : Set}
  {S-A : Setoid A} {S-B : Setoid B} {S-C : Setoid C} →
  SetoidMap S-B S-C →
  SetoidMap S-A S-B →
  SetoidMap S-A S-C
compose-SetoidMap g f = record
  { apply     = λ a → apply g (apply f a)
  ; respect-≈ = λ p → respect-≈ g (respect-≈ f p)
  }

------------------------------------------------------------------------
-- 3. Capstone for Set2.
--
-- SetoidMap + composition landed. Set3 specialises to
-- LanguageMorphism Setoids.
------------------------------------------------------------------------
