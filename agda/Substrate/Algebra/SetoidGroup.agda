------------------------------------------------------------------------
-- Substrate.Algebra.SetoidGroup
--
-- A group structure carried by a Setoid (i.e., the underlying type has
-- a propositional equivalence relation `_≈_` distinct from `_≡_`).
--
-- Substrate-native replacement for stdlib's `Algebra.Bundles.Group`
-- when the carrier's natural equality is *not* propositional (the
-- canonical example: pointwise-equal permutations of `A`).
--
-- The substrate's Substrate.Algebra.Group uses `_≡_`; this record
-- uses an explicit `_≈_` + the IsEquivalence witnesses + congruence
-- fields for `_∙_` and `_⁻¹`.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.SetoidGroup where

record SetoidGroup : Set₁ where
  field
    Carrier  : Set
    _≈_      : Carrier → Carrier → Set
    _∙_      : Carrier → Carrier → Carrier
    ε        : Carrier
    _⁻¹      : Carrier → Carrier
    -- Setoid equivalence on the carrier.
    ≈-refl   : (x : Carrier) → x ≈ x
    ≈-sym    : {x y : Carrier} → x ≈ y → y ≈ x
    ≈-trans  : {x y z : Carrier} → x ≈ y → y ≈ z → x ≈ z
    -- Group axioms up to ≈.
    ∙-assoc  :
      (x y z : Carrier) → ((x ∙ y) ∙ z) ≈ (x ∙ (y ∙ z))
    ε-left   : (x : Carrier) → (ε ∙ x) ≈ x
    ε-right  : (x : Carrier) → (x ∙ ε) ≈ x
    inv-left : (x : Carrier) → ((x ⁻¹) ∙ x) ≈ ε
    inv-right :
      (x : Carrier) → (x ∙ (x ⁻¹)) ≈ ε
    -- Congruences (operations respect ≈).
    ∙-cong   :
      {x₁ x₂ y₁ y₂ : Carrier} →
      x₁ ≈ x₂ → y₁ ≈ y₂ → (x₁ ∙ y₁) ≈ (x₂ ∙ y₂)
    ⁻¹-cong  :
      {x y : Carrier} → x ≈ y → (x ⁻¹) ≈ (y ⁻¹)

open SetoidGroup public
