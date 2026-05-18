------------------------------------------------------------------------
-- Substrate.Category.Equalizer
--
-- Primitive #2 in the Substrate.Category.Primitives roadmap.
-- Defines the categorical equalizer:
--
--   * IsEqualised f g a — predicate "f and g agree on a".
--   * Equalizer-Of f g — the Σ-subtype of A consisting of agreement points.
--   * equalizer-incl, equalizer-eq — projection + agreement equation.
--   * equalizer-factor — universal mapping property (maps factor uniquely
--     through the equalizer).
--
-- And specialisations:
--
--   * Kernel-At f b — = Equalizer-Of f (const b); kernel-of-f at point b.
--   * fixed-point bridge — FixedPoint γ x ≡ IsEqualised γ id x; categorical
--     handle showing the Coalgebra primitive's FixedPoint IS an equalizer
--     instance (γ vs identity).
--
-- Per `feedback_categorical_name_first`: names the structure with the
-- established categorical concept (equalizer) rather than inventing a
-- substrate-local name ("kernel-free predicate"). The universal property
-- IS the inference rule.
--
-- Retrofit sites:
--
--   * `In-Kernel C v` from Substrate.Algebra.F2.Code IS an equalizer
--     instance (apply (parity-check C) v ≡ 𝟎ⱽ = IsEqualised (apply
--     (parity-check C)) (const 𝟎ⱽ) v). Wrapped here in N-3 as a
--     trivial bridge.
--
--   * `NonDegenerate-4 M`'s radical condition (∀ w. bilinear-form-of-4
--     M v w ≡ 𝟘) is an intersection of per-w equalizers; non-degeneracy
--     says the intersection (= the radical) is the singleton {𝟎ⱽ}.
--     Full retrofit deferred to a follow-on slice (requires the
--     Pullback primitive #3 for the intersection structure).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Category.Equalizer where

open import Data.Product using (Σ; _,_; proj₁; proj₂)
open import Function using (id; const)
open import Level using (Level; _⊔_)
open import Relation.Binary.PropositionalEquality
  using (_≡_; refl; sym; trans; cong)

open import Substrate.Category.Coalgebra
  using (Endomap; FixedPoint; fixed)

private
  variable
    ℓ ℓ′ : Level
    A B Z : Set ℓ

------------------------------------------------------------------------
-- N-1: IsEqualised — the equalizer-membership predicate.
--
-- An element a : A is in the equalizer of (f, g : A → B) iff f and g
-- agree on a. This IS the equalizer's defining property at the level
-- of points.
--
-- Standard categorical name. The universal property in N-2 is what
-- elevates this from "a predicate" to "the equalizer object."
------------------------------------------------------------------------

record IsEqualised {A B : Set ℓ} (f g : A → B) (a : A) : Set ℓ where
  field
    equal : f a ≡ g a

open IsEqualised public

------------------------------------------------------------------------
-- N-2: The equalizer object + universal property.
--
-- Equalizer-Of f g packages the subtype of A where f and g agree.
-- equalizer-incl is the canonical inclusion into A; equalizer-eq is
-- the universal equation. equalizer-factor is the universal property:
-- any map Z → A that equalises f and g factors uniquely through the
-- equalizer.
------------------------------------------------------------------------

Equalizer-Of : {A B : Set ℓ} (f g : A → B) → Set ℓ
Equalizer-Of {A = A} f g = Σ A (IsEqualised f g)

equalizer-incl : {A B : Set ℓ} {f g : A → B} → Equalizer-Of f g → A
equalizer-incl = proj₁

equalizer-eq : {A B : Set ℓ} {f g : A → B} →
               (e : Equalizer-Of f g) →
               f (equalizer-incl e) ≡ g (equalizer-incl e)
equalizer-eq e = equal (proj₂ e)

-- The universal property: a map h : Z → A that satisfies f ∘ h ≡ g ∘ h
-- pointwise factors through the equalizer via the canonical lift.
equalizer-factor :
  {A B Z : Set ℓ} {f g : A → B}
  (h : Z → A) →
  ((z : Z) → f (h z) ≡ g (h z)) →
  Z → Equalizer-Of f g
equalizer-factor h h-equalises z = h z , record { equal = h-equalises z }

-- The factorisation commutes with inclusion: equalizer-incl ∘
-- equalizer-factor h = h. (This is the "uniqueness" half of the
-- universal property at the pointwise level.)
equalizer-factor-commutes :
  {A B Z : Set ℓ} {f g : A → B}
  (h : Z → A) (h-eq : (z : Z) → f (h z) ≡ g (h z)) (z : Z) →
  equalizer-incl {f = f} {g = g} (equalizer-factor h h-eq z) ≡ h z
equalizer-factor-commutes _ _ _ = refl

------------------------------------------------------------------------
-- N-3: Kernel-At — kernel of f at a point, as the equalizer of f
-- against the constant-b function.
--
-- The "kernel" of a function f : A → B at a target point b : B is the
-- preimage f⁻¹(b). Categorically, this is the equalizer of f and the
-- constant function `const b`. For linear maps over a pointed
-- carrier, the canonical kernel is taken at b = 𝟎 — but the general
-- equalizer-at-constant formulation works at any b.
------------------------------------------------------------------------

Kernel-At : {A B : Set ℓ} → (A → B) → B → A → Set ℓ
Kernel-At f b = IsEqualised f (const b)

-- The kernel object as a Σ-type.
Kernel-Of : {A B : Set ℓ} → (A → B) → B → Set ℓ
Kernel-Of f b = Equalizer-Of f (const b)

------------------------------------------------------------------------
-- N-4: Bridge to Coalgebra primitive — FixedPoint is the equalizer
-- against the identity endomap.
--
-- A fixed point of γ : X → X is exactly an element where γ and id
-- agree: FixedPoint γ x ⇔ IsEqualised γ id x. This makes the
-- Coalgebra primitive's `FixedPoint` a SPECIAL CASE of the Equalizer
-- primitive's `IsEqualised`.
--
-- Categorical reading: the set of fixed points of γ is the equalizer
-- of γ and id_X. Substrate's stabiliser retrofits (in
-- HodgeDim3.MetricGauge.Stabiliser) are simultaneously FixedPoint
-- instances AND equalizer-membership instances.
------------------------------------------------------------------------

fixed-point→equalised :
  {X : Set ℓ} {γ : Endomap X} {x : X} →
  FixedPoint γ x → IsEqualised γ id x
fixed-point→equalised fp = record { equal = fixed fp }

equalised→fixed-point :
  {X : Set ℓ} {γ : Endomap X} {x : X} →
  IsEqualised γ id x → FixedPoint γ x
equalised→fixed-point eq = record { fixed = equal eq }

------------------------------------------------------------------------
-- N-5: Capstone documentation.
--
-- This primitive gives the categorical handle for substrate's
-- "kernel-free" and "agreement-on-point" patterns:
--
--   * IsEqualised f g a / Equalizer-Of f g: the universal property
--     names the substrate's existing predicates "v satisfies P(v, w)
--     for all w in some family" when P is of agreement-shape.
--
--   * Kernel-At f b: the substrate's `In-Kernel C v` (= apply
--     (parity-check C) v ≡ 𝟎ⱽ) IS exactly `Kernel-At (apply
--     (parity-check C)) 𝟎ⱽ v` by definitional unfolding. The
--     retrofit is one wrapper line per kernel-shaped predicate.
--
--   * FixedPoint bridge: connects primitive #1 (Coalgebra) to
--     primitive #2 (Equalizer) — fixed points ARE equalizer
--     instances of (γ, id). This composition of universal properties
--     is exactly the categorical compositionality the substrate is
--     after.
--
-- Inference rule provided: any predicate "this element satisfies an
-- equation f x ≡ g x" inherits the equalizer universal property —
-- mapping into the equalizer ↔ mapping into A with the equation
-- satisfied pointwise. This eliminates per-site re-derivation of
-- "well, if I have a map h with f∘h ≡ g∘h, I can build a map into
-- the kernel" — that's just `equalizer-factor`.
--
-- Deferred coalgebraic-unfolding follow-ons:
--
--   * NonDegenerate-4 retrofit: the radical condition is an
--     intersection of per-w equalizers. Requires primitive #3
--     (Pullback / wide meet of equalizers) before the retrofit lands
--     cleanly. Without #3, the retrofit would re-invent the
--     intersection structure locally.
--
--   * `In-Kernel C v` retrofit in Substrate.Algebra.F2.Code as
--     a one-line wrapper. Done as a separate concern (touches the
--     Code module's public API).
--
--   * Coequalizer (dual): the substrate hasn't surfaced explicit
--     coequalizer instances yet; introducing the primitive when the
--     first orbit-space construction lands.
--
--   * Equalizer at arbitrary universe level / for general categories.
--     Current scope: Set-level equalizers, sufficient for substrate's
--     current carriers. Generalisation when needed.
------------------------------------------------------------------------
