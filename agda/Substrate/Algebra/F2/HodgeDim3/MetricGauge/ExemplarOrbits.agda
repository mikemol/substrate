------------------------------------------------------------------------
-- Substrate.Algebra.F2.HodgeDim3.MetricGauge.ExemplarOrbits
--
-- M-11.metric-gauge.exemplar-orbits slice. Extends the parent
-- MetricGauge.agda with a second concrete transitivity witness
-- (metric-id → metric-fully-coupled), demonstrating that all 3
-- structural exemplars from MetricGauge.agda are reachable from
-- metric-id and hence all in the same GL(3, F₂) congruence orbit.
--
-- After this file, we have witnessed:
--
--   metric-id ⊑ metric-mixed             (existing, MetricGauge.agda)
--   metric-id ⊑ metric-fully-coupled     (new, this file)
--
-- Symmetry (= for each forward T, the reverse T⁻¹) is a structural
-- consequence of GL(3, F₂) being a group, but formally requires the
-- inverse machinery — deferred to M-11.metric-gauge.orbit-equivalence-
-- relation (a separate coalgebraic-unfolding slice).
--
-- The 3-exemplar single-orbit claim is now demonstrated via
-- reachability from a common pivot (metric-id), per the gauge-
-- honesty discipline: any non-degenerate form is structurally
-- equivalent to any other via SOME T, all gauge-equivalent under
-- GL(3, F₂).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.F2.HodgeDim3.MetricGauge.ExemplarOrbits where

open import Substrate.Foundation.Fin using (Fin; zero; suc)
open import Substrate.Foundation.Fin.Literals using (₀; ₁; ₂; ₃; ₄; ₅)
open import Substrate.Foundation.Vec using ([]; _∷_; lookup)
open import Substrate.Foundation.Eq
  using (_≡_; refl; trans; cong)

open import Substrate.Algebra.F2
open import Substrate.Algebra.F2.Vector
open import Substrate.Algebra.F2.Linear
open import Substrate.Algebra.F2.Linear.FromImages
  using (linear-from-images; apply-linear-from-images-basis)
open import Substrate.Algebra.F2.HodgeDim3.MetricGauge

------------------------------------------------------------------------
-- N-1: T-id-to-fully-coupled.
--
-- Columns chosen to give T^T T = matrix of metric-fully-coupled:
--
--   t₀ = (1, 0, 0)   →  t₀·t₀ = 1   (a')
--   t₁ = (1, 1, 0)   →  t₁·t₁ = 0   (b')
--   t₂ = (1, 0, 1)   →  t₂·t₂ = 0   (c')
--   t₀·t₁ = 1                       (d')
--   t₀·t₂ = 1                       (e')
--   t₁·t₂ = 1                       (f')
--
-- So congruence-act T metric-id = (1, 0, 0, 1, 1, 1) = metric-fully-coupled.
--
-- Invertibility (det T = 1): the 3×3 matrix with these columns has
-- det = 1 in F₂ (verified by hand expansion); T is in GL(3, F₂).
------------------------------------------------------------------------

T-id-to-fully-coupled-images : Fin 3 → Vector 3
T-id-to-fully-coupled-images zero          = 𝟙 ∷ 𝟘 ∷ 𝟘 ∷ []
T-id-to-fully-coupled-images (suc zero)    = 𝟙 ∷ 𝟙 ∷ 𝟘 ∷ []
T-id-to-fully-coupled-images (suc (suc _)) = 𝟙 ∷ 𝟘 ∷ 𝟙 ∷ []

T-id-to-fully-coupled : Linear 3 3
T-id-to-fully-coupled = linear-from-images T-id-to-fully-coupled-images

------------------------------------------------------------------------
-- N-2: Per-basis apply reductions (universal-property discipline).
------------------------------------------------------------------------

T-fc-on-e₀ : apply T-id-to-fully-coupled (basis zero) ≡ (𝟙 ∷ 𝟘 ∷ 𝟘 ∷ [])
T-fc-on-e₀ = apply-linear-from-images-basis T-id-to-fully-coupled-images zero

T-fc-on-e₁ : apply T-id-to-fully-coupled (basis (suc zero)) ≡ (𝟙 ∷ 𝟙 ∷ 𝟘 ∷ [])
T-fc-on-e₁ = apply-linear-from-images-basis T-id-to-fully-coupled-images (suc zero)

T-fc-on-e₂ : apply T-id-to-fully-coupled (basis ₂) ≡ (𝟙 ∷ 𝟘 ∷ 𝟙 ∷ [])
T-fc-on-e₂ = apply-linear-from-images-basis T-id-to-fully-coupled-images ₂

------------------------------------------------------------------------
-- N-3: The transitivity witness equation.
--
-- Mechanically follows the template from
-- `congruence-id-to-mixed` in MetricGauge.agda: ≡-from-lookup on the 6
-- entries, each closing by `cong` over the T-fc-on-eᵢ helpers + F₂-
-- arithmetic evaluation by Agda.
------------------------------------------------------------------------

congruence-id-to-fully-coupled :
  congruence-act T-id-to-fully-coupled metric-id ≡ metric-fully-coupled
congruence-id-to-fully-coupled = ≡-from-lookup _ _ goal
  where
    goal : (i : Fin 6) →
           lookup (congruence-act T-id-to-fully-coupled metric-id) i ≡
           lookup metric-fully-coupled i
    goal zero =
      -- a' = bilinear-form-of metric-id (T e₀) (T e₀)
      -- After T-fc-on-e₀: = bilinear-form-of metric-id (1,0,0) (1,0,0) = 1
      cong (λ x → bilinear-form-of metric-id x x) T-fc-on-e₀
    goal (suc zero) =
      -- b' = (1,1,0)·(1,1,0) = 0
      cong (λ x → bilinear-form-of metric-id x x) T-fc-on-e₁
    goal ₂ =
      -- c' = (1,0,1)·(1,0,1) = 0
      cong (λ x → bilinear-form-of metric-id x x) T-fc-on-e₂
    goal ₃ =
      -- d' = (1,0,0)·(1,1,0) = 1
      trans (cong (λ x → bilinear-form-of metric-id x (apply T-id-to-fully-coupled (basis (suc zero)))) T-fc-on-e₀)
            (cong (bilinear-form-of metric-id (𝟙 ∷ 𝟘 ∷ 𝟘 ∷ [])) T-fc-on-e₁)
    goal ₄ =
      -- e' = (1,0,0)·(1,0,1) = 1
      trans (cong (λ x → bilinear-form-of metric-id x (apply T-id-to-fully-coupled (basis ₂))) T-fc-on-e₀)
            (cong (bilinear-form-of metric-id (𝟙 ∷ 𝟘 ∷ 𝟘 ∷ [])) T-fc-on-e₂)
    goal ₅ =
      -- f' = (1,1,0)·(1,0,1) = 1
      trans (cong (λ x → bilinear-form-of metric-id x (apply T-id-to-fully-coupled (basis ₂))) T-fc-on-e₁)
            (cong (bilinear-form-of metric-id (𝟙 ∷ 𝟙 ∷ 𝟘 ∷ [])) T-fc-on-e₂)

------------------------------------------------------------------------
-- N-4: Status documentation.
--
-- With this slice, we have witnessed both:
--
--   congruence-act T-id-to-mixed         metric-id ≡ metric-mixed
--   congruence-act T-id-to-fully-coupled metric-id ≡ metric-fully-coupled
--
-- These pivot through metric-id to establish that all 3 structural
-- exemplars (metric-id, metric-mixed, metric-fully-coupled) are in
-- the same GL(3, F₂) congruence orbit.
--
-- The "pivot through metric-id" pattern is the standard way to
-- demonstrate orbit-connectedness when symmetry is implicit: showing
-- A ↦ B via a single base-point B works for ANY orbit element A. To
-- formally conclude X ↔ Y for X, Y ≠ base, we'd compose via B-to-X
-- and Y-to-B; the latter requires the inverse of B-to-Y.
--
-- Deferred (coalgebraic-unfolding follow-on slices):
--
--   * M-11.metric-gauge.orbit-equivalence-relation: define
--     Reach / Orbit-Equiv as a relation type; refl + trans
--     achievable here, sym requires the GL inverse machinery.
--
--   * M-11.metric-gauge.congruence-compose: the structural lemma
--     congruence-act (T₂ ∘L T₁) M ≡ congruence-act T₁ (congruence-act T₂ M),
--     needed for transitivity-via-Linear-composition (= constructing
--     "mixed → fully-coupled" as T-id-to-fully-coupled ∘L (T-id-to-mixed)⁻¹).
--
--   * M-11.metric-gauge.orbit-characterisation-full: Gram-Schmidt-like
--     normalisation showing EVERY non-degenerate symmetric form
--     reduces to metric-id via some T ∈ GL(3, F₂). The structural
--     single-orbit theorem for ALL 28 forms. This is the "main theorem"
--     of the metric-gauge program; the present slice + the existing
--     MetricGauge.agda + the deferred follow-ons compose into it.
--
-- See M-11.metric-gauge.exemplar-orbits.DBE.md for slice scoping; the
-- parent M-11.metric-gauge.DBE.md catalogs the full set of deferred
-- coalgebraic-unfolding slices.
------------------------------------------------------------------------
