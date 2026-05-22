------------------------------------------------------------------------
-- Substrate.Algebra.F2.HodgeDim4.MetricGauge.HodgeRecast
--
-- M-11.metric-gauge.dim4.hodge-recast slice. Dim-4 analog of
-- HodgeDim3.MetricGauge.HodgeRecast.
--
-- Before this slice: at n=4, `_·F_ : Vector 4 → Vector 4 → F₂` was
-- the standard sum-of-products dot product, used implicitly by every
-- HodgeDim4 construction (Bivector, HodgeStar, SelfDual,
-- ReservedBridge) WITHOUT acknowledging that this is one of the many
-- non-degenerate symmetric bilinear forms over F₂⁴ — a gauge choice.
--
-- After this slice: at n=4, `_·F_ v w ≡ bilinear-form-of-4 metric-id-4 v w`
-- explicitly. The recasting exposes the implicit gauge choice, making
-- the substrate gauge-honest about its dim-4 Hodge structure.
-- Alternative metrics (or any other non-degenerate form) give
-- structurally different bilinear forms / orthogonality structures
-- under GL(4, F₂).
--
-- Per `feedback_choice_rigidification_in_substrate`: every implicit
-- gauge is rigidification by neglect; surfacing it IS the work
-- (per `feedback_coalgebraic_not_consumer_driven`).
--
-- Proof template inherited from dim-3 HodgeRecast: expand LHS
-- (sum-F₂ over Fin 4, right-associated with trailing 𝟘) and RHS
-- (bilinear-form-of-4 metric-id-4 expansion, left-associated with
-- residual +𝟘's after Agda's pattern reductions), bridge through
-- canonical form `((v₀·w₀ + v₁·w₁) + v₂·w₂) + v₃·w₃` via +-assoc and
-- +-identityʳ chains.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.F2.HodgeDim4.MetricGauge.HodgeRecast where

open import Substrate.Foundation.Vec using ([]; _∷_)
open import Substrate.Foundation.Eq
  using (_≡_; refl; sym; trans; cong; cong₂)

open import Substrate.Algebra.F2
open import Substrate.Algebra.F2.Vector
open import Substrate.Algebra.F2.Vector.DotProduct using (_·F_)
open import Substrate.Algebra.F2.HodgeDim4.MetricGauge

------------------------------------------------------------------------
-- N-1: The recast lemma.
--
-- At n=4, the standard dot product `_·F_` equals
-- `bilinear-form-of-4 metric-id-4`.
--
-- Both sides unfold to v₀·w₀ + v₁·w₁ + v₂·w₂ + v₃·w₃ after F₂
-- arithmetic. LHS comes from sum-F₂ over Fin 4 (right-assoc with
-- trailing 𝟘); RHS comes from bilinear-form-of-4 instantiated at
-- metric-id-4's all-ones diagonal (left-assoc with residual +𝟘's
-- after Agda's `𝟘 + y = y`, `𝟙 · y = y`, and `𝟘 · _ = 𝟘` reductions).
------------------------------------------------------------------------

-- DEMOTED to instantiation. The original ~50-LoC LHS→canonical /
-- RHS←canonical bridging proof at dim 4 (per-row residual-𝟘
-- cleanups + outer assoc/identity manipulations) is now a one-line
-- corollary of the generic HodgeRecast (`·F-eq-metric-id-bilin-generic`
-- in Substrate.Algebra.F2.SymBilinForm.HodgeRecast) chained with the
-- bilinear-form-of-metric-id-4-bridge from GenericBridge.
--
-- Original proof preserved in git history at c8a1c8c (dim4.hodge-recast
-- pre-demotion commit).

open import Substrate.Algebra.F2.SymBilinForm.HodgeRecast
  using (·F-eq-metric-id-bilin-generic)
open import Substrate.Algebra.F2.HodgeDim4.MetricGauge.GenericBridge
  using (bilinear-form-of-metric-id-4-bridge)

·F-eq-metric-id-4-bilin :
  (v w : Vector 4) → v ·F w ≡ bilinear-form-of-4 metric-id-4 v w
·F-eq-metric-id-4-bilin v w =
  trans (·F-eq-metric-id-bilin-generic v w)
        (sym (bilinear-form-of-metric-id-4-bridge v w))


------------------------------------------------------------------------
-- N-2: Concrete demonstration of metric-dependence at dim 4.
--
-- Under metric-id-4 (= the gauge `_·F_` implicitly uses), e₀ and e₁
-- are orthogonal. This is the standard dim-4 dot-product orthogonality
-- recovered as the metric-id-4 instance of bilinear-form-of-4.
--
-- Concrete demonstrations under non-trivial dim-4 metrics defer to
-- a follow-on slice (which would introduce metric-mixed-4 /
-- metric-fully-coupled-4 exemplars in the dim-4 metric-gauge).
------------------------------------------------------------------------

e₀-perp-e₁-under-metric-id-4 :
  bilinear-form-of-4 metric-id-4
    (𝟙 ∷ 𝟘 ∷ 𝟘 ∷ 𝟘 ∷ []) (𝟘 ∷ 𝟙 ∷ 𝟘 ∷ 𝟘 ∷ []) ≡ 𝟘
e₀-perp-e₁-under-metric-id-4 = refl

-- And via `_·F_` (which the recast lemma proves is the same thing):
e₀-perp-e₁-via-·F-at-dim-4 :
  (𝟙 ∷ 𝟘 ∷ 𝟘 ∷ 𝟘 ∷ []) ·F (𝟘 ∷ 𝟙 ∷ 𝟘 ∷ 𝟘 ∷ []) ≡ 𝟘
e₀-perp-e₁-via-·F-at-dim-4 = refl

------------------------------------------------------------------------
-- N-3: Capstone documentation.
--
-- The existing dim-4 `_·F_` is now formally recognized as the
-- metric-id-4 instance of a gauge-parametric family of symmetric
-- bilinear forms over F₂⁴. Every dim-4 HodgeDim4 construction
-- (Bivector orthogonality, HodgeStar at n=4, SelfDual subspace,
-- ReservedBridge codeword identification) implicitly inherits the
-- metric-id-4 gauge choice.
--
-- Per the L_metric meta-level at dim 4: the gauge-family of
-- non-degenerate SymBilinForm-4 (~280 elements in the "split"
-- Witt-class orbit under GL(4, F₂); see HodgeDim4/MetricGauge
-- capstone) now parametrises the existing Hodge structures. The
-- catalog's "8-element SelfDual = Reserved" identification IS
-- the metric-id-4 instance of a 280-element gauge family of
-- 8-element subspaces, all gauge-equivalent under GL(4, F₂).
--
-- Alternative metrics give:
--   * Different orthogonality structures on F₂⁴
--   * Different Hodge ★ at Λ²(F₂⁴) (different self-dual / anti-
--     self-dual bivector splits)
--   * Different `Reserved`-style identifications at the codeword
--     level
--
-- Recasting `_·F_` as the metric-id-4 instance does NOT change the
-- existing dim-4 code's behavior — it surfaces the previously-
-- implicit gauge choice, making the substrate gauge-honest about it.
--
-- Deferred coalgebraic-unfolding follow-ons:
--
--   * MetricOrthogonality-4: define `metric-orthogonal-4 M v w =
--     bilinear-form-of-4 M v w ≡ 𝟘`. Dim-4 analog of the dim-3
--     MetricOrthogonality slice. One-line definition + recast
--     lemmas + concrete demos.
--
--   * Metric-parametric Bivector / HodgeStar / SelfDual at dim 4:
--     lift the existing implicit metric-id-4 dependence to
--     parametric `bilinear-form-of-4 M`-based versions. Each
--     downstream Hodge construction takes M : SymBilinForm-4 (with
--     NonDegenerate-4 M when invertibility is needed) and produces
--     the metric-specific version.
--
--   * Metric-parametric ReservedBridge: lift the catalog's
--     "Reserved = SelfDual" identification to a metric-parametric
--     bridge, exposing the 280-element gauge family of such
--     identifications.
--
--   * Exemplar metrics at dim 4 (metric-mixed-4, metric-fully-
--     coupled-4 analogs of the dim-3 exemplars) for concrete
--     demonstrations of metric-dependent orthogonality flips.
--
-- See agda/Substrate/Cocycles/M-11.metric-gauge.DBE.md for the full
-- dim-4 metric-gauge roadmap (when it gets written) and
-- M-11.metric-gauge.dim4-foundation's capstone for the dependency
-- order.
------------------------------------------------------------------------
