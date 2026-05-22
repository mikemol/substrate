------------------------------------------------------------------------
-- Substrate.Category.Coherence
--
-- CD1 of the Coherence-Discharge arc per
-- [scratch/higher_cat_arc_plan.md].
--
-- The substrate's coherence-record framework: when a categorical
-- structure (monoidal, braided, bicategorical, double, ...) is
-- equipped with a "coherence diagram" that asserts an equation
-- between morphisms, this record bundles the diagram's TWO sides
-- + the WITNESS of their equality at a chosen equivalence.
--
-- The framework is universal: pentagon/triangle/hexagon/interchange
-- are all instances. CD2-CD20 specialise it.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Category.Coherence where

open import Substrate.Foundation.Eq using (_≡_; refl; sym; trans)

------------------------------------------------------------------------
-- 1. The generic CoherenceDiagram record.
--
-- A coherence diagram at a type T with equivalence _≈_ is a pair
-- of T-valued sides and a witness that they are ≈-equal.
------------------------------------------------------------------------

record CoherenceDiagram
  (T : Set)
  (_≈_ : T → T → Set)
  : Set where
  field
    lhs     : T
    rhs     : T
    commute : lhs ≈ rhs

open CoherenceDiagram public

------------------------------------------------------------------------
-- 2. Strict coherence: the diagram commutes propositionally.
--
-- The specialisation _≈_ = _≡_; refl-discharge is the canonical
-- strict-instance proof.
------------------------------------------------------------------------

StrictCoherence : (T : Set) → Set
StrictCoherence T = CoherenceDiagram T _≡_

strict-refl :
  {T : Set} (t : T) → StrictCoherence T
strict-refl t = record { lhs = t ; rhs = t ; commute = refl }

------------------------------------------------------------------------
-- 3. Coherence transport: composing two coherence diagrams.
--
-- If `lhs₁ ≈ rhs₁` and `rhs₁ ≈ rhs₂`, then `lhs₁ ≈ rhs₂` (at any
-- transitive equivalence).
------------------------------------------------------------------------

compose-≡-coherence :
  {T : Set} (a b c : T) → a ≡ b → b ≡ c → a ≡ c
compose-≡-coherence _ _ _ = trans

------------------------------------------------------------------------
-- 4. Capstone for CD1.
--
-- The coherence framework lands here. CD2-CD20 supply concrete
-- instances: interchange (CD2), adjunction-triangles (CD3),
-- pentagon (CD5/CD9), triangle (CD6/CD10), hexagon (CD7), etc.
------------------------------------------------------------------------
