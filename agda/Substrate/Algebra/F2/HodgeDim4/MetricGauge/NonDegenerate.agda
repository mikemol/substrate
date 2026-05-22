------------------------------------------------------------------------
-- Substrate.Algebra.F2.HodgeDim4.MetricGauge.NonDegenerate
--
-- DEMOTED to instantiation. The per-basis kernel-free witness for
-- metric-id-4 (171 LoC of pair-metric-id-4-with-eᵢ helpers +
-- componentwise extraction) is now a corollary of the generic
-- metric-id-non-degenerate-generic proven once at any n in
-- Substrate.Algebra.F2.SymBilinForm.NonDegenerate.
--
-- The bridge between the dim-4-specific `bilinear-form-of-4 metric-id-4`
-- and the generic `bilinear-form-of metric-id` is constructed via the
-- two HodgeRecast lemmas at v and w: both definitions equal `v ·F w`,
-- so they equal each other.
--
-- Original 171-LoC proof (with 4 `pair-metric-id-4-with-eᵢ` helpers
-- each chaining ·-absorbʳ + +-identity{ˡ,ʳ} cleanups for residual
-- F₂-pattern reductions) preserved in git history at d843d8a / 43abf11
-- pre-demotion commits.
--
-- Retained from the original slice:
--
--   * `Radical-as-WideMeet-4` — the categorical retrofit naming the
--     radical condition as a Wide-Meet of per-w equalizers. This was
--     the primitive #3 (Pullback) retrofit at dim 4 and remains
--     useful as a bridge to the categorical primitives even after
--     the demotion.
--
-- After this slice:
--
--   * `metric-id-4-non-degenerate` is a 5-line derivation, not a
--     171-line proof.
--   * The 4 `pair-metric-id-4-with-eᵢ` helpers are no longer needed
--     (and removed).
--   * No external module depended on the helpers (per audit grep);
--     the deletion is safe.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.F2.HodgeDim4.MetricGauge.NonDegenerate where

open import Substrate.Foundation.Vec using ([]; _∷_)
open import Substrate.Foundation.Function using (const)
open import Substrate.Foundation.Eq
  using (_≡_; refl; sym; trans)

open import Substrate.Algebra.F2
open import Substrate.Algebra.F2.Vector
open import Substrate.Algebra.F2.Vector.DotProduct using (_·F_)
open import Substrate.Algebra.F2.HodgeDim4.MetricGauge

-- Generic infrastructure.
open import Substrate.Algebra.F2.SymBilinForm
  using () renaming (bilinear-form-of to bf-generic;
                     metric-id        to metric-id-generic;
                     Radical          to Radical-generic;
                     pair-eq-family   to pair-eq-family-generic)
open import Substrate.Algebra.F2.SymBilinForm.NonDegenerate.MetricIdNonDegenerate
  using (metric-id-non-degenerate-generic)
open import Substrate.Algebra.F2.SymBilinForm.HodgeRecast
  using (·F-eq-metric-id-bilin-generic)

-- The dim-4 HodgeRecast — bridges bilinear-form-of-4 metric-id-4 to _·F_.
open import Substrate.Algebra.F2.HodgeDim4.MetricGauge.HodgeRecast
  using (·F-eq-metric-id-4-bilin)

open import Substrate.Category.Equalizer using (IsEqualised; equal)
open import Substrate.Category.Pullback using (Wide-Meet)

------------------------------------------------------------------------
-- N-1: metric-id-4-non-degenerate as instantiation of the generic
-- theorem.
--
-- Path: given hyp : (w) → bilinear-form-of-4 metric-id-4 v w ≡ 𝟘,
-- bridge to (w) → bf-generic metric-id-generic v w ≡ 𝟘 via the
-- two-recast chain (both equal `v ·F w`). Then apply
-- metric-id-non-degenerate-generic.
------------------------------------------------------------------------

metric-id-4-non-degenerate : NonDegenerate-4 metric-id-4
metric-id-4-non-degenerate v hyp =
  metric-id-non-degenerate-generic v radical
  where
    -- Bridge: bf-generic metric-id-generic v w ≡ bilinear-form-of-4 metric-id-4 v w
    -- via `≡ v ·F w` from both directions.
    bridge : (w : Vector 4) →
             bf-generic metric-id-generic v w
               ≡ bilinear-form-of-4 metric-id-4 v w
    bridge w = trans (sym (·F-eq-metric-id-bilin-generic v w))
                     (·F-eq-metric-id-4-bilin v w)

    -- Build the Radical-generic witness pointwise from hyp.
    radical : Radical-generic metric-id-generic v
    radical w = record { equal = trans (bridge w) (hyp w) }

------------------------------------------------------------------------
-- N-2: Pullback-primitive retrofit (retained from prior slice).
--
-- The dim-4 radical condition is the Wide-Meet over w of the per-w
-- equalizer family. Categorical handle for the substrate's recurring
-- "∀ w. predicate(v, w)" pattern.
------------------------------------------------------------------------

-- The per-w equalizer family for a bilinear form M at dim 4.
M-pair-eq-family-4 : SymBilinForm-4 → Vector 4 → Vector 4 → Set
M-pair-eq-family-4 M w v =
  IsEqualised (λ u → bilinear-form-of-4 M u w) (const 𝟘) v

-- The radical of M as a Wide-Meet of the per-w equalizer family.
Radical-as-WideMeet-4 : SymBilinForm-4 → Vector 4 → Set
Radical-as-WideMeet-4 M = Wide-Meet (M-pair-eq-family-4 M)

-- Two-direction bridges between the existing inner-condition form
-- and Wide-Meet form.
radical-from-existing :
  (M : SymBilinForm-4) (v : Vector 4) →
  ((w : Vector 4) → bilinear-form-of-4 M v w ≡ 𝟘) →
  Radical-as-WideMeet-4 M v
radical-from-existing M v pair-zero w = record { equal = pair-zero w }

radical-to-existing :
  (M : SymBilinForm-4) (v : Vector 4) →
  Radical-as-WideMeet-4 M v →
  (w : Vector 4) → bilinear-form-of-4 M v w ≡ 𝟘
radical-to-existing M v radical w = equal (radical w)

------------------------------------------------------------------------
-- N-3: Capstone — demotion achieved.
--
-- Before this slice:
--   * 171 LoC of pair-metric-id-4-with-eᵢ helpers + componentwise
--     ≡-from-lookup extraction.
--   * Each pair-metric-id-4-with-eᵢ was a 6-step chain of ·-absorbʳ
--     + +-identity{ˡ,ʳ} cleaning F₂-pattern residue.
--
-- After this slice:
--   * `metric-id-4-non-degenerate` is a 5-line instantiation of the
--     generic theorem.
--   * The bridge is constructed by chaining two HodgeRecast lemmas
--     (no fresh algebraic work needed).
--
-- Per `feedback_categorical_name_first`: the generic theorem
-- + the recast bridges + the existing dim-4 HodgeRecast jointly
-- derive the dim-4 non-degeneracy. Per-dim re-proof is unnecessary
-- once the generic + bridge infrastructure is in place.
--
-- The Radical-as-WideMeet-4 retrofit (N-2) names the radical
-- condition categorically via the Pullback primitive (Wide-Meet),
-- and is independent of the demotion above.
------------------------------------------------------------------------
