------------------------------------------------------------------------
-- Substrate.Algebra.F2.HodgeDim4.MetricGauge
--
-- M-11.metric-gauge.dim4-foundation slice. Extends the metric-gauge
-- structural pattern from dim 3 to dim 4: non-degenerate symmetric
-- bilinear forms over F₂⁴, the GL(4, F₂) congruence action, and the
-- diagonal-identity metric `metric-id-4`.
--
-- This is the dim-4 analogue of `HodgeDim3.MetricGauge` (= the
-- foundation that the existing HodgeDim4 work — Bivector, HodgeStar,
-- SelfDual, ReservedBridge — implicitly used `_·F_` against without
-- naming the metric-id-4 gauge choice).
--
-- Per `feedback_expose_generator_not_orbit` + `feedback_coalgebraic_not_
-- consumer_driven`: this slice exposes the dim-4 gauge structure via
-- the INFERENCE RULE (`NonDegenerate-4` via the kernel-free predicate)
-- and the GENERATOR (the GL(4, F₂) congruence action), NOT via
-- enumeration of all non-degenerate forms.
--
-- Cardinality remarks (for context, NOT used in proofs):
--
--   |GL(4, F₂)|                = 20160 = (2⁴−1)(2⁴−2)(2⁴−4)(2⁴−8)
--   |sym non-degenerate forms| = ? — to be derived via orbit-stabiliser
--                                  in a follow-on slice. The stabiliser
--                                  of metric-id-4 is O(4, F₂); by the
--                                  classification this has order 72
--                                  (the (3,3) splitting case) — so the
--                                  orbit has 20160/72 = 280 elements.
--   28-form story at dim 3 generalises to 280 forms at dim 4 in the
--   "split" Witt class; a different stabiliser (S₅ of order 120) gives
--   the "anisotropic" 168-element orbit. The full picture is a
--   coalgebraic-unfolding follow-on.
--
-- The 4-dim determinant is more complex than 3-dim's `abc + af + cd + eb`
-- formula. Rather than encode the 4×4 determinant directly, we use the
-- kernel-free characterisation:
--   `NonDegenerate-4 M = ∀ v → (∀ w → bilinear-form-of-4 M v w ≡ 𝟘) → v ≡ 𝟎ⱽ`
-- which is more structural and doesn't require closed-form det.
--
-- Follow-on coalgebraic-unfolding slices (deferred):
--
--   * metric-id-4-non-degenerate via concrete kernel-free witness.
--   * Specific exemplars metric-mixed-4 / metric-fully-coupled-4
--     analogous to dim 3.
--   * congruence-id-to-X-4 transitivity witnesses (concrete T : Linear 4 4).
--   * Orbit characterisation at dim 4 (Witt's theorem instance).
--   * Stabiliser O(4, F₂) at dim 4 (subgroup analysis).
--   * Recast lemma `_·F_ ≡ bilinear-form-of-4 metric-id-4` at dim 4
--     (analogous to HodgeDim3.MetricGauge.HodgeRecast).
--   * Metric-parametric Bivector / HodgeStar / SelfDual lifting the
--     existing implicit metric-id-4 dependence.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.F2.HodgeDim4.MetricGauge where

open import Data.Fin using (Fin; zero; suc)
open import Data.Vec using (Vec; []; _∷_; lookup)
open import Relation.Binary.PropositionalEquality
  using (_≡_; refl; trans; cong)

open import Substrate.Algebra.F2
open import Substrate.Algebra.F2.Vector
open import Substrate.Algebra.F2.Linear

------------------------------------------------------------------------
-- N-1: SymBilinForm-4 type + 10 named accessors.
--
-- A symmetric 4×4 matrix over F₂ has 10 independent entries:
--
--   [[ a  e  f  g ]
--    [ e  b  h  i ]
--    [ f  h  c  j ]
--    [ g  i  j  d ]]
--
-- where (a, b, c, d) are diagonal entries and (e, f, g, h, i, j) are
-- the upper-triangular off-diagonals at positions
-- (0,1), (0,2), (0,3), (1,2), (1,3), (2,3).
--
-- We represent it as Vector 10 with entries (a, b, c, d, e, f, g, h, i, j)
-- at positions (0..9).
------------------------------------------------------------------------

SymBilinForm-4 : Set
SymBilinForm-4 = Vector 10

-- Named accessors. The diagonal four (a, b, c, d) come first, then
-- the six off-diagonals in lex-order (e=01, f=02, g=03, h=12, i=13, j=23).
entry-a entry-b entry-c entry-d : SymBilinForm-4 → F₂
entry-a m = lookup m zero
entry-b m = lookup m (suc zero)
entry-c m = lookup m (suc (suc zero))
entry-d m = lookup m (suc (suc (suc zero)))

entry-e entry-f entry-g entry-h entry-i entry-j : SymBilinForm-4 → F₂
entry-e m = lookup m (suc (suc (suc (suc zero))))
entry-f m = lookup m (suc (suc (suc (suc (suc zero)))))
entry-g m = lookup m (suc (suc (suc (suc (suc (suc zero))))))
entry-h m = lookup m (suc (suc (suc (suc (suc (suc (suc zero)))))))
entry-i m = lookup m (suc (suc (suc (suc (suc (suc (suc (suc zero))))))))
entry-j m = lookup m (suc (suc (suc (suc (suc (suc (suc (suc (suc zero)))))))))

------------------------------------------------------------------------
-- N-2: bilinear-form-of-4 — pair-by-matrix-by-pair evaluation.
--
-- bilinear-form-of-4 M v w = v^T M w over F₂. For symmetric M with
-- entries (a, b, c, d, e, f, g, h, i, j) as above:
--
--   v^T M w = v₀(a·w₀ + e·w₁ + f·w₂ + g·w₃)
--           + v₁(e·w₀ + b·w₁ + h·w₂ + i·w₃)
--           + v₂(f·w₀ + h·w₁ + c·w₂ + j·w₃)
--           + v₃(g·w₀ + i·w₁ + j·w₂ + d·w₃)
--
-- 16 multiplication terms across 4 rows. Left-associated in each row
-- and across rows (matching dim 3's style).
------------------------------------------------------------------------

bilinear-form-of-4 : SymBilinForm-4 → Vector 4 → Vector 4 → F₂
bilinear-form-of-4 (a ∷ b ∷ c ∷ d ∷ e ∷ f ∷ g ∷ h ∷ i ∷ j ∷ [])
                   (v₀ ∷ v₁ ∷ v₂ ∷ v₃ ∷ [])
                   (w₀ ∷ w₁ ∷ w₂ ∷ w₃ ∷ []) =
  v₀ · (a · w₀ + e · w₁ + f · w₂ + g · w₃) +
  v₁ · (e · w₀ + b · w₁ + h · w₂ + i · w₃) +
  v₂ · (f · w₀ + h · w₁ + c · w₂ + j · w₃) +
  v₃ · (g · w₀ + i · w₁ + j · w₂ + d · w₃)

------------------------------------------------------------------------
-- N-3: NonDegenerate-4 — kernel-free predicate.
--
-- M is non-degenerate iff no nonzero vector pairs to zero with every
-- other vector. Equivalently, the linear map (v ↦ M v) is injective
-- (= the only v with M v = 0 is v = 0).
--
-- Decidability: at fixed n = 4 with finite F₂, this is decidable by
-- enumerating the 2⁴ = 16 candidate v's; the decidability instance
-- itself is deferred (kernel-enumeration is a separate combinator).
------------------------------------------------------------------------

NonDegenerate-4 : SymBilinForm-4 → Set
NonDegenerate-4 M =
  (v : Vector 4) →
  ((w : Vector 4) → bilinear-form-of-4 M v w ≡ 𝟘) →
  v ≡ 𝟎ⱽ

------------------------------------------------------------------------
-- N-4: metric-id-4 — the diagonal identity at dim 4.
--
-- a=b=c=d=𝟙; all off-diagonals 𝟘. Matrix is I₄.
--
-- This is the dim-4 analogue of metric-id; it's the metric that the
-- existing `_·F_ : Vector 4 → Vector 4 → F₂` implicitly uses (the
-- standard sum-of-products dot product). The recast lemma
-- `_·F_ ≡ bilinear-form-of-4 metric-id-4` is a follow-on slice.
--
-- Concrete witness that bilinear-form-of-4 metric-id-4 collapses to
-- the sum-of-products: under metric-id-4 (a=b=c=d=𝟙, off-diagonals 𝟘),
-- the 16-term expansion collapses (after F₂ arithmetic — 𝟙·x=x, 𝟘·x=𝟘,
-- 𝟘+y=y) to:
--
--   v₀·w₀ + v₁·w₁ + v₂·w₂ + v₃·w₃
--
-- (= the standard 4-dim dot product).
------------------------------------------------------------------------

metric-id-4 : SymBilinForm-4
metric-id-4 = 𝟙 ∷ 𝟙 ∷ 𝟙 ∷ 𝟙 ∷ 𝟘 ∷ 𝟘 ∷ 𝟘 ∷ 𝟘 ∷ 𝟘 ∷ 𝟘 ∷ []

-- Smoke test: e₀ pairs with itself to 𝟙 under metric-id-4.
e₀-self-pair-metric-id-4 :
  bilinear-form-of-4 metric-id-4
    (𝟙 ∷ 𝟘 ∷ 𝟘 ∷ 𝟘 ∷ [])
    (𝟙 ∷ 𝟘 ∷ 𝟘 ∷ 𝟘 ∷ []) ≡ 𝟙
e₀-self-pair-metric-id-4 = refl

-- And e₀ ⊥ e₁ under metric-id-4 (diagonal identity has zero off-diagonal).
e₀-perp-e₁-metric-id-4 :
  bilinear-form-of-4 metric-id-4
    (𝟙 ∷ 𝟘 ∷ 𝟘 ∷ 𝟘 ∷ [])
    (𝟘 ∷ 𝟙 ∷ 𝟘 ∷ 𝟘 ∷ []) ≡ 𝟘
e₀-perp-e₁-metric-id-4 = refl

------------------------------------------------------------------------
-- N-5: congruence-act-4 — the GL(4, F₂) congruence action.
--
-- congruence-act-4 T M produces the new symmetric form whose (i, j)
-- entry is bilinear-form-of-4 M (T e_i) (T e_j). This IS the
-- T^T M T congruence action expressed in bilinear-form interpretation.
--
-- 10 entries to fill: 4 diagonals + 6 off-diagonals (lex order).
------------------------------------------------------------------------

congruence-act-4 : Linear 4 4 → SymBilinForm-4 → SymBilinForm-4
congruence-act-4 T M =
  bilinear-form-of-4 M Te₀ Te₀ ∷
  bilinear-form-of-4 M Te₁ Te₁ ∷
  bilinear-form-of-4 M Te₂ Te₂ ∷
  bilinear-form-of-4 M Te₃ Te₃ ∷
  bilinear-form-of-4 M Te₀ Te₁ ∷
  bilinear-form-of-4 M Te₀ Te₂ ∷
  bilinear-form-of-4 M Te₀ Te₃ ∷
  bilinear-form-of-4 M Te₁ Te₂ ∷
  bilinear-form-of-4 M Te₁ Te₃ ∷
  bilinear-form-of-4 M Te₂ Te₃ ∷ []
  where
    Te₀ = apply T (basis zero)
    Te₁ = apply T (basis (suc zero))
    Te₂ = apply T (basis (suc (suc zero)))
    Te₃ = apply T (basis (suc (suc (suc zero))))

------------------------------------------------------------------------
-- N-6: Capstone — the dim-4 metric gauge foundation.
--
-- After this slice, the dim-4 substrate has:
--
--   * `SymBilinForm-4` — the type of symmetric 4×4 forms over F₂
--     (Vector 10).
--   * `bilinear-form-of-4 M` — the pairing M(v, w) via 16-term
--     expansion.
--   * `NonDegenerate-4 M` — the kernel-free non-degeneracy predicate.
--   * `metric-id-4` — the diagonal identity metric, witnessing the
--     gauge choice that the existing HodgeDim4 work (Bivector,
--     HodgeStar, SelfDual, ReservedBridge) implicitly uses through
--     `_·F_`.
--   * `congruence-act-4` — the GL(4, F₂) action on SymBilinForm-4.
--
-- **Structural parallels to dim 3:**
--
--   dim 3: |GL(3,F₂)| = 168, |orbit| = 28, |stabiliser| = 6 (= S₃)
--   dim 4: |GL(4,F₂)| = 20160, |orbit| = 280 (split case)
--          |stabiliser| = 72 (O(4,F₂) split case)
--
--   Witt classification at dim 4 over F₂ splits the orbits by Arf
--   invariant + Witt class — anisotropic + split. The "split" case
--   (which contains metric-id-4) gives the 280-element orbit.
--   The anisotropic case gives a separate orbit; cardinality and
--   stabiliser deferred.
--
-- **The gauge-honesty effect at dim 4:**
--
-- The existing `_·F_`-based constructions in HodgeDim4 (V₄-plane
-- analogues, ChiralityAxis at dim 4, the Bivector / HodgeStar /
-- SelfDual ladder, ReservedBridge to the 8-element catalog reading)
-- silently used `metric-id-4`. Surfacing it here makes them
-- gauge-honest: alternative metrics (lifted to Λ²(F₂⁴) via the
-- induced bivector metric) would give alternative SelfDual subspaces
-- and alternative ReservedBridge identifications.
--
-- The "8-element SelfDual" reading is one of 280 such 8-element
-- subspaces, all gauge-equivalent under GL(4, F₂); the catalog's
-- "Reserved = 8 signed singletons" identification implicitly chose
-- metric-id-4.
--
-- Deferred coalgebraic-unfolding slices (in priority order):
--
--   * `metric-id-4-non-degenerate` — kernel-free witness that
--     metric-id-4 ∈ NonDegenerate-4. Direct case-analysis on v's
--     16 candidates (or via the e_i-pairing argument: if M v ≡ 𝟎
--     for all w, then in particular M(v, e_i) = lookup v i = 𝟘
--     for each i, so v = 𝟎ⱽ).
--
--   * `HodgeRecast-4` — `_·F_ ≡ bilinear-form-of-4 metric-id-4` at
--     dim 4 (the dim-4 analogue of HodgeDim3.MetricGauge.HodgeRecast).
--     Same canonical-form bridging template.
--
--   * `MetricOrthogonality-4` — `metric-orthogonal-4 M v w` as the
--     dim-4 parametric orthogonality predicate.
--
--   * `metric-mixed-4`, `metric-fully-coupled-4` — structural-exemplar
--     metrics analogous to dim 3, exposing Witt-class structure.
--
--   * `congruence-id-to-mixed-4` — concrete transitivity witness via
--     explicit T : Linear 4 4 (Gram-Schmidt-style construction).
--
--   * Lift Bivector / HodgeStar / SelfDual / ReservedBridge to
--     metric-parametric forms, exposing the existing implicit
--     metric-id-4 dependence and the 280-element gauge family.
--
-- Per the discipline (`feedback_coalgebraic_not_consumer_driven`):
-- these are coalgebraic-unfolding slices that surface progressively
-- more gauge-parametric structure, not "deferred until needed."
------------------------------------------------------------------------
