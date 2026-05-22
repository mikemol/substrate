------------------------------------------------------------------------
-- Substrate.Category.Coalgebra
--
-- Primitive #1 in the Substrate.Category.Primitives roadmap.
-- Defines the categorical primitives for endomap coalgebras:
--
--   * FixedPoint γ x — the property that γ fixes x.
--   * InvariantSubset γ S — the property that S is closed under γ.
--   * The singleton-fixed-point ↔ invariant-subset bridge.
--   * FixedPoint-of-compose — derived inference rule that compositions
--     of fixed-point-preserving endomaps preserve fixed points.
--
-- Per `feedback_categorical_name_first`: this names with the
-- established categorical concept (subcoalgebra of an endomap = invariant
-- subset; fixed point = singleton invariant subset) rather than inventing
-- a substrate-local name ("coalgebraic-stability"). The universal property
-- IS the inference rule.
--
-- The substrate's existing stabiliser work (in HodgeDim3/MetricGauge/
-- Stabiliser.agda and StabiliserClosure.agda) re-witnesses the same
-- structure per-generator. With this primitive in place, the per-generator
-- proofs become FixedPoint instances; closure under group composition
-- follows from FixedPoint-of-compose plus an action-composition lemma
-- (currently `congruence-compose`, a deferred slice in the metric-gauge
-- roadmap).
--
-- Scope discipline: this slice introduces the ENDOMAP-coalgebra case
-- (= F-coalgebra for F = Identity). General F-coalgebra (`Subcoalgebra
-- F : F-Coalgebra → Subobject → Set`) is a follow-on slice — substrate-
-- discipline says don't add scaffold for hypothetical future generality.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Category.Coalgebra where

open import Level using (Level; _⊔_)
open import Substrate.Foundation.Eq
  using (_≡_; refl; sym; trans; cong)

private
  variable
    ℓ ℓ′ : Level
    X : Set ℓ

------------------------------------------------------------------------
-- The endomap coalgebra (= F-coalgebra for F = Identity).
--
-- A coalgebra of the identity endofunctor on Set is just an endomap
-- γ : X → X. We give it a type-alias to keep the categorical framing
-- visible at use sites.
------------------------------------------------------------------------

Endomap : Set ℓ → Set ℓ
Endomap X = X → X

------------------------------------------------------------------------
-- Fixed point of an endomap.
--
-- Standard categorical name. An x : X is a fixed point of γ : Endomap X
-- iff γ x ≡ x. The universal property: a fixed point is an arrow
-- 1 → X equalising γ and identity (equalizer formulation), or
-- equivalently a γ-coalgebra map from the terminal coalgebra (1, id).
------------------------------------------------------------------------

record FixedPoint {X : Set ℓ} (γ : Endomap X) (x : X) : Set ℓ where
  field
    fixed : γ x ≡ x

open FixedPoint public

------------------------------------------------------------------------
-- Invariant subset under an endomap = subcoalgebra of (X, γ) for the
-- identity endofunctor.
--
-- A subobject S ⊆ X (here represented as a predicate S : X → Set) is
-- INVARIANT under γ iff γ(x) ∈ S whenever x ∈ S. Equivalently: the
-- restriction γ ↾ S factors through S. This is exactly the subcoalgebra
-- universal property in the F = Identity case.
------------------------------------------------------------------------

record InvariantSubset {X : Set ℓ} (γ : Endomap X) (S : X → Set ℓ′) :
                       Set (ℓ ⊔ ℓ′) where
  field
    closure : (x : X) → S x → S (γ x)

open InvariantSubset public

------------------------------------------------------------------------
-- The singleton-fixed-point bridge.
--
-- A fixed point x of γ corresponds to the singleton predicate {x} being
-- invariant under γ. Both directions hold.
--
-- This is the categorical bridge between the "single element fixed by
-- γ" framing (used by substrate's stabiliser work) and the "subset
-- closed under γ" framing (the general subcoalgebra concept).
------------------------------------------------------------------------

-- The singleton predicate at x.
Singleton : {X : Set ℓ} → X → X → Set ℓ
Singleton x y = y ≡ x

-- Fixed point ⇒ singleton is invariant.
fixed-point→invariant-singleton :
  {X : Set ℓ} {γ : Endomap X} {x : X} →
  FixedPoint γ x → InvariantSubset {ℓ′ = ℓ} γ (Singleton x)
fixed-point→invariant-singleton {γ = γ} {x = x} fp =
  record { closure = λ y y≡x → trans (cong γ y≡x) (fixed fp) }

-- Singleton is invariant ⇒ fixed point.
invariant-singleton→fixed-point :
  {X : Set ℓ} {γ : Endomap X} {x : X} →
  InvariantSubset {ℓ′ = ℓ} γ (Singleton x) → FixedPoint γ x
invariant-singleton→fixed-point {x = x} inv =
  record { fixed = closure inv x refl }

------------------------------------------------------------------------
-- Derived inference rule: composition of fixed-point-preserving
-- endomaps preserves fixed points.
--
-- This is the categorical fact that fixed-point witnesses compose
-- along endomap composition. In the substrate's stabiliser context,
-- it says: if x is fixed by γ₁ AND γ₂, then x is fixed by γ₁ ∘ γ₂.
--
-- For the metric-id stabiliser: combined with the (deferred)
-- congruence-compose lemma, this gives the StabiliserClosure cascade
-- for free — every composition of stabiliser generators is itself a
-- stabiliser, without re-proving each composition.
------------------------------------------------------------------------

-- Endomap composition (categorical).
_∘E_ : {X : Set ℓ} → Endomap X → Endomap X → Endomap X
(γ₁ ∘E γ₂) x = γ₁ (γ₂ x)

infixr 9 _∘E_

FixedPoint-of-compose :
  {X : Set ℓ} {γ₁ γ₂ : Endomap X} {x : X} →
  FixedPoint γ₁ x → FixedPoint γ₂ x → FixedPoint (γ₁ ∘E γ₂) x
FixedPoint-of-compose {γ₁ = γ₁} {γ₂ = γ₂} {x = x} fp₁ fp₂ =
  record { fixed = trans (cong γ₁ (fixed fp₂)) (fixed fp₁) }

------------------------------------------------------------------------
-- Capstone documentation.
--
-- This primitive provides the categorical handles for substrate's
-- coalgebraic stability observations:
--
--   * FixedPoint γ x: the "x is stabilised by γ" pattern. Universal
--     property: FixedPoint γ x ⇔ singleton {x} is γ-invariant.
--
--   * InvariantSubset γ S: the "S is closed under γ" pattern, =
--     subcoalgebra of (X, γ) in the F = Identity F-coalgebra case.
--
--   * FixedPoint-of-compose: derived inference rule. Composes fixed-
--     point witnesses along endomap composition. The substrate's
--     StabiliserClosure 3-cycle witness becomes a derived corollary of
--     this rule + congruence-compose (deferred).
--
-- Retrofit sites scheduled (per Primitives.DBE.md):
--
--   1. s₁-stabilises-metric-id, s₂-stabilises-metric-id, and
--      s₁∘s₂-stabilises-metric-id wrap as FixedPoint instances in
--      Substrate.Algebra.F2.HodgeDim3.MetricGauge.Stabiliser.
--
--   2. Once `congruence-compose : congruence-act (T₁ ∘L T₂) ≡
--      congruence-act T₁ ∘E congruence-act T₂` lands, the
--      StabiliserClosure 3-cycle proof reduces to one line via
--      FixedPoint-of-compose + congruence-compose. The full 6-element
--      S₃ stabiliser becomes derivable mechanically from the 2 Coxeter
--      generators' FixedPoint witnesses.
--
-- Deferred coalgebraic-unfolding follow-ons:
--
--   * General F-coalgebra subcoalgebra (`Subcoalgebra F` for any
--     endofunctor F on Set). The Identity-case version here is sufficient
--     for the substrate's current endomap-based work; the general case
--     is a follow-on when the substrate's coalgebraic discipline starts
--     using non-trivial F.
--
--   * Coequalizer (dual to Equalizer, scheduled as primitive #2). The
--     coequalizer of γ and identity is the "orbit space under γ" — the
--     coalgebraic dual to FixedPoint's equalizer formulation.
--
--   * G-equivariance: when γ is the action of a group element, a fixed
--     point at every g ∈ G is a G-fixed point. The substrate's stabiliser
--     subgroup IS the set of g with `FixedPoint (congruence-act g) x`;
--     surfacing this as a categorical group-action primitive is a
--     natural follow-on once the substrate's group-action infrastructure
--     stabilises.
------------------------------------------------------------------------
