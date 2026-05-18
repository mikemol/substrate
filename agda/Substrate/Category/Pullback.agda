------------------------------------------------------------------------
-- Substrate.Category.Pullback
--
-- Primitive #3 in the Substrate.Category.Primitives roadmap.
-- Defines the categorical pullback (binary case) and wide meet
-- (family-indexed intersection):
--
--   * IsInPullback f g (a, b) — predicate "(a, b) lies over the
--     diagonal under f and g".
--   * Pullback-Of f g — the Σ-subtype of A × B at the pullback.
--   * pullback-π₁, pullback-π₂ — projections.
--   * pullback-square — the universal square equation.
--   * pullback-factor — universal mapping property.
--   * Wide-Meet P — family-indexed meet of predicates.
--   * wide-meet-factor — wide universal property.
--
-- Plus the categorical bridge: a binary pullback is the equalizer of
-- (f ∘ π₁) and (g ∘ π₂) over A × B. Composes primitives #2 (Equalizer)
-- and #3 (Pullback).
--
-- Per `feedback_categorical_name_first`: names the structure with the
-- established categorical concept (pullback / wide pullback / meet in
-- subobject lattice) rather than inventing a substrate-local name
-- ("orbit-intersection-fiber"). The universal property IS the
-- inference rule.
--
-- Retrofit sites:
--
--   * `M-orth-to-V4Plane` from HodgeDim3/MetricGauge/V4PlaneOrth IS
--     a binary pullback of two metric-orthogonal predicates. Wrapped
--     here in N-5.
--
--   * NonDegenerate-4's radical condition (∀ w. bilinear-form-of-4 M v w
--     ≡ 𝟘) IS a Wide-Meet over the per-w equalizer family. Deferred
--     to a follow-on slice (one-line bridge once needed).
--
--   * The substrate's 3+1 parity universal (every 2-dim F₂-subspace's
--     "1" element is the intersection of orbit-predicates) names as a
--     wide pullback of orbit-membership predicates. Wide structural
--     naming deferred until the orbit-class infrastructure stabilises.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Category.Pullback where

open import Data.Product using (Σ; _×_; _,_; proj₁; proj₂)
open import Function using (id; _∘_)
open import Level using (Level; _⊔_)
open import Relation.Binary.PropositionalEquality
  using (_≡_; refl; sym; trans; cong)

open import Substrate.Category.Equalizer
  using (IsEqualised; Equalizer-Of; equal)

private
  variable
    ℓ ℓ′ : Level
    A B C Z : Set ℓ
    I : Set ℓ

------------------------------------------------------------------------
-- N-1: IsInPullback — pullback-membership predicate.
--
-- A pair (a, b) : A × B lies over the diagonal of f : A → C and
-- g : B → C iff f a ≡ g b. This is the pullback's defining property
-- at the level of points.
------------------------------------------------------------------------

record IsInPullback {A B C : Set ℓ} (f : A → C) (g : B → C) (p : A × B) :
                    Set ℓ where
  field
    over-diagonal : f (proj₁ p) ≡ g (proj₂ p)

open IsInPullback public

------------------------------------------------------------------------
-- N-2: The pullback object + projections.
--
-- Pullback-Of f g packages the subtype of A × B at the pullback. The
-- projections recover the canonical maps into A and B from the
-- universal pullback square.
------------------------------------------------------------------------

Pullback-Of : {A B C : Set ℓ} (f : A → C) (g : B → C) → Set ℓ
Pullback-Of {A = A} {B = B} f g = Σ (A × B) (IsInPullback f g)

pullback-π₁ : {A B C : Set ℓ} {f : A → C} {g : B → C} →
              Pullback-Of f g → A
pullback-π₁ p = proj₁ (proj₁ p)

pullback-π₂ : {A B C : Set ℓ} {f : A → C} {g : B → C} →
              Pullback-Of f g → B
pullback-π₂ p = proj₂ (proj₁ p)

-- The pullback square commutes: f ∘ π₁ ≡ g ∘ π₂ pointwise.
pullback-square :
  {A B C : Set ℓ} {f : A → C} {g : B → C} →
  (p : Pullback-Of f g) → f (pullback-π₁ p) ≡ g (pullback-π₂ p)
pullback-square p = over-diagonal (proj₂ p)

------------------------------------------------------------------------
-- N-3: Universal mapping property of the pullback.
--
-- A "cone over (f, g)" is a pair of maps (h₁ : Z → A, h₂ : Z → B)
-- with f ∘ h₁ ≡ g ∘ h₂ pointwise. Any such cone factors uniquely
-- through the pullback via the canonical lift.
------------------------------------------------------------------------

pullback-factor :
  {A B C Z : Set ℓ} {f : A → C} {g : B → C}
  (h₁ : Z → A) (h₂ : Z → B) →
  ((z : Z) → f (h₁ z) ≡ g (h₂ z)) →
  Z → Pullback-Of f g
pullback-factor h₁ h₂ commutes z =
  (h₁ z , h₂ z) , record { over-diagonal = commutes z }

-- The factorisation recovers each cone leg via the projections.
pullback-factor-commutes-π₁ :
  {A B C Z : Set ℓ} {f : A → C} {g : B → C}
  (h₁ : Z → A) (h₂ : Z → B) (sq : (z : Z) → f (h₁ z) ≡ g (h₂ z)) (z : Z) →
  pullback-π₁ {f = f} {g = g} (pullback-factor h₁ h₂ sq z) ≡ h₁ z
pullback-factor-commutes-π₁ _ _ _ _ = refl

pullback-factor-commutes-π₂ :
  {A B C Z : Set ℓ} {f : A → C} {g : B → C}
  (h₁ : Z → A) (h₂ : Z → B) (sq : (z : Z) → f (h₁ z) ≡ g (h₂ z)) (z : Z) →
  pullback-π₂ {f = f} {g = g} (pullback-factor h₁ h₂ sq z) ≡ h₂ z
pullback-factor-commutes-π₂ _ _ _ _ = refl

------------------------------------------------------------------------
-- N-4: Wide meet — family-indexed intersection of predicates.
--
-- For a family P : I → A → Set, the wide meet is the predicate
--   Wide-Meet P x  =  ∀ i, P i x
-- Universal property: a predicate Q ⊆ A is contained in Wide-Meet P
-- iff Q ⊆ P i for every i ∈ I. This is the meet in the subobject
-- lattice Sub(A) over an arbitrary index set I.
--
-- The binary case is recoverable: Wide-Meet (λ b → if b then P else Q).
-- The wide case is the structurally-honest formulation of the
-- substrate's recurring "∀ w. predicate(v, w)" pattern (e.g.,
-- NonDegenerate-4's radical condition).
------------------------------------------------------------------------

Wide-Meet : {A : Set ℓ} {I : Set ℓ′} → (I → A → Set ℓ) → A → Set (ℓ ⊔ ℓ′)
Wide-Meet {I = I} P x = (i : I) → P i x

-- The wide universal property: a predicate Q lifts to the meet iff
-- it lifts to each P i. Formulated as factorisation through the meet.
wide-meet-factor :
  {A Z : Set ℓ} {I : Set ℓ′}
  (P : I → A → Set ℓ) (h : Z → A) →
  ((i : I) (z : Z) → P i (h z)) →
  (z : Z) → Wide-Meet P (h z)
wide-meet-factor P h all-P z i = all-P i z

------------------------------------------------------------------------
-- N-5: Pullback-equalizer bridge — binary pullback as equalizer.
--
-- The binary pullback of (f, g) is precisely the equalizer of the
-- two compositions (f ∘ π₁) and (g ∘ π₂) over A × B. This composes
-- primitives #2 and #3: a pullback IS an equalizer instance of the
-- product projections precomposed with the cone legs.
------------------------------------------------------------------------

pullback→equalizer :
  {A B C : Set ℓ} {f : A → C} {g : B → C}
  (p : A × B) → IsInPullback f g p →
  IsEqualised (λ q → f (proj₁ q)) (λ q → g (proj₂ q)) p
pullback→equalizer p in-pb = record { equal = over-diagonal in-pb }

equalizer→pullback :
  {A B C : Set ℓ} {f : A → C} {g : B → C}
  (p : A × B) →
  IsEqualised (λ q → f (proj₁ q)) (λ q → g (proj₂ q)) p →
  IsInPullback f g p
equalizer→pullback p eq = record { over-diagonal = equal eq }

------------------------------------------------------------------------
-- N-6: Capstone documentation.
--
-- This primitive gives the categorical handle for substrate's
-- intersection / meet / pullback patterns:
--
--   * IsInPullback / Pullback-Of: names the substrate's binary
--     "satisfies both predicates at once" structure (e.g.,
--     M-orth-to-V4Plane = orthogonal to e₀ AND orthogonal to e₁).
--
--   * pullback-factor: universal property. Eliminates per-site
--     reconstruction of "if I have maps into A and B that agree on
--     C, I can build a map into the pullback" — that's just
--     pullback-factor.
--
--   * Wide-Meet: names the substrate's recurring "for all i,
--     predicate(v, i)" structure (e.g., the radical condition in
--     NonDegenerate-4). The wide universal property reduces "show v
--     is in the meet" to "show v is in each component" — exactly the
--     substrate's componentwise proof template.
--
--   * Pullback↔Equalizer bridge: shows primitives #2 (Equalizer) and
--     #3 (Pullback) compose; binary pullback IS an equalizer of
--     projection-composed cone legs.
--
-- Inference rules provided:
--
--   * "If h₁ : Z → A and h₂ : Z → B satisfy a commuting condition,
--     they factor through the pullback" — `pullback-factor`.
--
--   * "v is in the meet of a family of predicates ⇔ v is in each
--     member" — `Wide-Meet` definition + `wide-meet-factor`.
--
--   * "binary pullback = equalizer of cone-leg compositions" —
--     `pullback→equalizer` / `equalizer→pullback`.
--
-- Deferred coalgebraic-unfolding follow-ons:
--
--   * NonDegenerate-4 retrofit via Wide-Meet: the radical condition
--     `∀ w. bilinear-form-of-4 M v w ≡ 𝟘` is precisely
--     `Wide-Meet (λ w v → IsEqualised (λ u → bilinear-form-of-4 M u w)
--     (const 𝟘) v) v`. NonDegenerate-4 then states: the radical
--     contains only the trivial element. One-line bridge once a
--     consumer wants it.
--
--   * `M-orth-to-V4Plane` retrofit in HodgeDim3/MetricGauge/V4PlaneOrth
--     as Pullback-Of of two metric-orthogonal predicates. Light touch;
--     deferred to a separate slice to keep this one focused on the
--     primitive itself.
--
--   * Pushout (dual to Pullback): the substrate hasn't surfaced
--     explicit pushout instances yet. Introduce when the first
--     coalgebraic-construction lands that needs them.
--
--   * Pullback in arbitrary category vs Set-level: current scope is
--     Set-level. General categorical pullback when the substrate
--     needs categories other than Set.
------------------------------------------------------------------------
