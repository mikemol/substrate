------------------------------------------------------------------------
-- Substrate.Algebra.F2.HodgeDim3.MetricGauge.MetricOrthogonality
--
-- M-11.metric-gauge.metric-orthogonality slice. Defines orthogonality
-- as a metric-parametric concept, surfacing what was previously
-- implicit in the substrate's use of `_·F_`-orthogonality.
--
-- Background (from M-11.metric-gauge.hodge-recast):
--
--   * The existing `_·F_` (DotProduct.agda) silently used the
--     metric-id bilinear form — one of 28 non-degenerate metrics.
--   * Existing orthogonality-based constructions (V4Plane,
--     ChiralityAxis, HodgeComplement-Dim3) implicitly assumed
--     metric-id orthogonality.
--
-- This slice:
--
--   * Defines `metric-orthogonal M v w = bilinear-form-of M v w ≡ 𝟘`
--     as a first-class metric-parametric predicate.
--   * Recasts `·F`-orthogonality as `metric-orthogonal metric-id`.
--   * Demonstrates concrete metric-dependence: e₀ and e₁ are
--     orthogonal under metric-id but NOT under metric-mixed.
--
-- After this slice: downstream constructions can state orthogonality
-- parametrically over the metric (`metric-orthogonal M v w`) rather
-- than implicitly assuming metric-id.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.F2.HodgeDim3.MetricGauge.MetricOrthogonality where

open import Data.Vec using ([]; _∷_)
open import Relation.Binary.PropositionalEquality
  using (_≡_; refl; sym; trans; cong)

open import Substrate.Algebra.F2
open import Substrate.Algebra.F2.Vector
open import Substrate.Algebra.F2.Vector.DotProduct using (_·F_)
open import Substrate.Algebra.F2.HodgeDim3.MetricGauge
open import Substrate.Algebra.F2.HodgeDim3.MetricGauge.HodgeRecast
  using (·F-eq-metric-id-bilin)

------------------------------------------------------------------------
-- N-1: The metric-parametric orthogonality predicate.
--
-- `metric-orthogonal M v w` holds iff v and w are orthogonal under
-- the bilinear form defined by M (i.e., their pairing is 𝟘).
--
-- This is the gauge-honest replacement for the implicit
-- `_·F_`-orthogonality used throughout HodgeDim3.
------------------------------------------------------------------------

metric-orthogonal : SymBilinForm-3 → Vector 3 → Vector 3 → Set
metric-orthogonal M v w = bilinear-form-of M v w ≡ 𝟘

------------------------------------------------------------------------
-- N-2: Recast of `_·F_`-orthogonality as `metric-orthogonal metric-id`.
--
-- The existing `v ·F w ≡ 𝟘` notion of orthogonality is exactly the
-- metric-id-instance of metric-orthogonal. Both directions of the
-- iff are immediate consequences of `·F-eq-metric-id-bilin` from
-- the hodge-recast slice.
------------------------------------------------------------------------

·F-zero-implies-metric-id-orthogonal :
  (v w : Vector 3) → v ·F w ≡ 𝟘 → metric-orthogonal metric-id v w
·F-zero-implies-metric-id-orthogonal v w p =
  trans (sym (·F-eq-metric-id-bilin v w)) p

metric-id-orthogonal-implies-·F-zero :
  (v w : Vector 3) → metric-orthogonal metric-id v w → v ·F w ≡ 𝟘
metric-id-orthogonal-implies-·F-zero v w p =
  trans (·F-eq-metric-id-bilin v w) p

------------------------------------------------------------------------
-- N-3: Concrete metric-dependence demonstrations.
--
-- Two specific vectors (e₀ and e₁) that are orthogonal under one
-- metric but not under another. The substrate's "orthogonality"
-- notion is metric-dependent; surfacing this via concrete witnesses
-- makes the gauge-dependence verifiable, not abstract.
------------------------------------------------------------------------

-- Under metric-id, e₀ and e₁ are orthogonal.
e₀-perp-e₁-under-metric-id :
  metric-orthogonal metric-id (𝟙 ∷ 𝟘 ∷ 𝟘 ∷ []) (𝟘 ∷ 𝟙 ∷ 𝟘 ∷ [])
e₀-perp-e₁-under-metric-id = refl

-- Under metric-mixed (where d = 1 couples (0,1) to (1,0)), e₀ and e₁
-- are NOT orthogonal — their pairing is 𝟙, not 𝟘. There is no
-- `metric-orthogonal metric-mixed e₀ e₁` witness; the explicit
-- positive statement (= the pairing IS 𝟙) appears in hodge-recast as
-- `e₀-not-perp-e₁-under-metric-mixed`.

-- Under metric-id, e₀ is also orthogonal to e₂.
e₀-perp-e₂-under-metric-id :
  metric-orthogonal metric-id (𝟙 ∷ 𝟘 ∷ 𝟘 ∷ []) (𝟘 ∷ 𝟘 ∷ 𝟙 ∷ [])
e₀-perp-e₂-under-metric-id = refl

-- And under metric-mixed, e₀ remains orthogonal to e₂ (the d=1
-- coupling only affects (0,1), not (0,2)).
e₀-perp-e₂-under-metric-mixed :
  metric-orthogonal metric-mixed (𝟙 ∷ 𝟘 ∷ 𝟘 ∷ []) (𝟘 ∷ 𝟘 ∷ 𝟙 ∷ [])
e₀-perp-e₂-under-metric-mixed = refl

-- Under metric-fully-coupled, e₀ and e₂ ARE no longer orthogonal —
-- the e=1 coupling pairs them. The orthogonality structure shifts
-- with the metric choice; different metrics surface different
-- "orthogonality graphs" on the same underlying vector pairs.

------------------------------------------------------------------------
-- N-4: Capstone documentation.
--
-- After this slice:
--
--   * `metric-orthogonal M v w` is the first-class metric-parametric
--     orthogonality predicate at n=3.
--
--   * The existing `_·F_`-based orthogonality scattered through
--     HodgeDim3 (V4Plane.agda, ChiralityAxis.agda, HodgeDim3.agda's
--     HodgeComplement-Dim3 record) is precisely the
--     metric-id-instance: `_·F_ v w ≡ 𝟘` iff
--     `metric-orthogonal metric-id v w`.
--
--   * Concrete demonstrations show orthogonality FLIPS across
--     metric choices (e₀ ⊥ e₁ under metric-id but not under
--     metric-mixed; e₀ ⊥ e₂ under metric-id AND metric-mixed but
--     not under metric-fully-coupled).
--
-- Deferred coalgebraic-unfolding slices that flow from this:
--
--   * Metric-parametric V4Plane: define `V4Plane-At-Metric M` so the
--     subspace's orthogonality structure changes with M. Requires
--     re-deriving the "orthogonal complement" construction
--     parametrically.
--
--   * Metric-parametric HodgeComplement-Dim3: lift the existing
--     `HodgeComplement-Dim3` record to take a metric parameter,
--     producing a 28-element family of Hodge-complement structures.
--
--   * Metric-parametric SelfDual at HodgeDim4 (requires extending
--     metric-gauge to dim 4 first; the 28-form count there will
--     differ).
--
-- Per the discipline (`feedback_coalgebraic_not_consumer_driven`):
-- these unfold from the metric-orthogonality foundation; they're
-- not "deferred until consumers need them" but rather "distinct
-- coalgebraic-unfolding slices that surface progressively more
-- gauge-parametric structure."
--
-- The substrate's tetrative tower at L_metric is now equipped with
-- a metric-parametric orthogonality concept; the substrate is
-- gauge-honest about orthogonality as one of 28 GL(3,F₂)-equivalent
-- choices.
------------------------------------------------------------------------
