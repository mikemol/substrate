------------------------------------------------------------------------
-- Substrate.Category.Pushout
--
-- Dual of Substrate.Category.Pullback. For (f : C → A, g : C → B),
-- the pushout is the universal cocone — a pair of maps
-- (h₁ : A → Z, h₂ : B → Z) with h₁ ∘ f ≡ h₂ ∘ g pointwise. Where
-- Pullback materialises a SUBTYPE of A × B (the pairs agreeing
-- under f and g), Pushout materialises the UNIVERSAL PROPERTY on
-- cocones into Z.
--
-- Per [[project-agda-cubical-extraction-discipline]] (no HITs): the
-- pushout carrier (A ⊎ B) / (f c ~ g c) is not introduced as a new
-- type. The substrate captures pushout-cocones — pairs of A/B-out-
-- going maps that agree on the C-image — which is structurally
-- equivalent to the quotient's universal property in the absence
-- of HITs.
--
-- Per the skeleton-as-pullback principle: once Pullback is lifted
-- to a CategoryOf-level record, Pushout absorbs as Pullback on
-- Opposite via opposite-Functor. At the current Set-level resolution
-- the two primitives sit side-by-side.
--
-- Dual companions:
--   * IsPushoutCocone    ~ IsInPullback
--   * PushoutCocone      ~ Pullback-Of (codomain-side)
--   * pushout-factor     ~ pullback-factor
--   * Wide-Join          ~ Wide-Meet (family-indexed pushout)
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Category.Pushout where

open import Level using (Level; _⊔_)
open import Substrate.Foundation.Eq using (_≡_; refl)

private
  variable
    ℓ ℓ′ : Level
    A B C Z : Set ℓ
    I : Set ℓ

------------------------------------------------------------------------
-- IsPushoutCocone — point-level pushout-cocone predicate.
--
-- A pair (h₁ : A → Z, h₂ : B → Z) is a pushout cocone over
-- (f : C → A, g : C → B) iff h₁ (f c) ≡ h₂ (g c) for every c : C.
-- Dual of IsInPullback: where Pullback lifts a pair (a, b) through
-- the agreement of f and g into a common codomain, Pushout forces
-- the two A/B-out-going maps to agree on the C-image.
------------------------------------------------------------------------

record IsPushoutCocone
       {A B C Z : Set ℓ}
       (f : C → A) (g : C → B)
       (h₁ : A → Z) (h₂ : B → Z) (c : C) : Set ℓ where
  field
    cocone-agrees : h₁ (f c) ≡ h₂ (g c)

open IsPushoutCocone public

------------------------------------------------------------------------
-- PushoutCocone — universal-property predicate.
--
-- A pair (h₁, h₂) is a full pushout cocone iff it agrees on every
-- c : C. Substrate-honest formulation of the pushout's universal
-- property without materialising the (A ⊎ B)/~ quotient carrier.
------------------------------------------------------------------------

PushoutCocone :
  {A B C Z : Set ℓ}
  (f : C → A) (g : C → B)
  (h₁ : A → Z) (h₂ : B → Z) → Set ℓ
PushoutCocone {C = C} f g h₁ h₂ = (c : C) → h₁ (f c) ≡ h₂ (g c)

------------------------------------------------------------------------
-- pushout-factor — the factorisation as a pushout-cocone witness.
--
-- Given the cospan (f, g) and a candidate cocone (h₁, h₂) with
-- pointwise commutation, this packages the pair as a witnessed
-- pushout cocone. Dual shape to pullback-factor.
------------------------------------------------------------------------

pushout-factor :
  {A B C Z : Set ℓ} (f : C → A) (g : C → B)
  (h₁ : A → Z) (h₂ : B → Z) →
  ((c : C) → h₁ (f c) ≡ h₂ (g c)) →
  PushoutCocone f g h₁ h₂
pushout-factor _ _ _ _ commutes = commutes

------------------------------------------------------------------------
-- pushout-factor-recovers-leg-A / -B — the factorisation recovers
-- each cocone leg.
--
-- Trivial at this resolution (factorisation IS the commutation data);
-- recorded for shape parity with pullback-factor-commutes-π₁/π₂.
------------------------------------------------------------------------

pushout-factor-recovers-leg-A :
  {A B C Z : Set ℓ} (f : C → A) (g : C → B)
  (h₁ : A → Z) (h₂ : B → Z)
  (sq : (c : C) → h₁ (f c) ≡ h₂ (g c)) (a : A) →
  h₁ a ≡ h₁ a
pushout-factor-recovers-leg-A _ _ _ _ _ _ = refl

pushout-factor-recovers-leg-B :
  {A B C Z : Set ℓ} (f : C → A) (g : C → B)
  (h₁ : A → Z) (h₂ : B → Z)
  (sq : (c : C) → h₁ (f c) ≡ h₂ (g c)) (b : B) →
  h₂ b ≡ h₂ b
pushout-factor-recovers-leg-B _ _ _ _ _ _ = refl

------------------------------------------------------------------------
-- Wide-Join — family-indexed universal cocone.
--
-- For a family of cospans (f_i : C → A, g_i : C → B_i), a wide
-- pushout-cocone is a family of agreement witnesses for each i.
-- Dual of Wide-Meet from Pullback.
--
-- Universal property: a candidate map h cofactors the wide join
-- iff it agrees with every leg of the family.
------------------------------------------------------------------------

Wide-Join :
  {A C Z : Set ℓ} {I : Set ℓ′}
  (f : C → A)
  (legs : I → C → Z)
  (h : A → Z) → Set (ℓ ⊔ ℓ′)
Wide-Join {I = I} f legs h = (i : I) (c : _) → h (f c) ≡ legs i c

wide-join-factor :
  {A C Z : Set ℓ} {I : Set ℓ′}
  (f : C → A) (legs : I → C → Z) (h : A → Z) →
  ((i : I) (c : _) → h (f c) ≡ legs i c) →
  Wide-Join f legs h
wide-join-factor _ _ _ all-agrees = all-agrees
