------------------------------------------------------------------------
-- Substrate.Algebra.F2.HodgeDim3.MetricGauge.StabiliserClosure
--
-- DEMOTED to instantiation. The per-cycle proof of
-- `s₁∘s₂-stabilises-metric-id` (originally 166 LoC of per-basis
-- `apply-s₁∘s₂-on-eᵢ` helpers + ≡-from-lookup case-by-case extraction)
-- is now a 3-line derivation:
--
--   trans (congruence-compose-3 s₁ s₂ metric-id)
--         (trans (cong (congruence-act s₂) s₁-stabilises-metric-id)
--                s₂-stabilises-metric-id)
--
-- — i.e., the dim-3 specific composition law (from CongruenceBridge)
-- + the two Coxeter-generator FixedPoint witnesses (from Stabiliser).
--
-- Same pattern derives the remaining 3 stabiliser elements (s₂∘L s₁,
-- s₁∘L s₂∘L s₁, s₂∘L s₁∘L s₂) mechanically. The full 6-element S₃
-- stabiliser of metric-id under GL(3, F₂) congruence is now derivable
-- from the 2 Coxeter generators alone, without per-cycle algebraic
-- proof.
--
-- Per `feedback_categorical_name_first`: the dim-3 specific
-- composition law (congruence-compose-3) IS the inference rule
-- coming from the generic CongruenceCompose; combined with
-- FixedPoint-of-compose (primitive #1) it automates the closure
-- cascade.
--
-- Original 166-LoC proof preserved in git history at 075f5f4
-- (stabiliser-closure-3-cycle commit).
--
-- **Structural payoff at L_metric (unchanged):**
--
--   |GL(3, F₂)|         = 168
--   |orbit(metric-id)|  = 28
--   |stabiliser|        = 6  (Coxeter S₃; the 2 Coxeter generators
--                              are the only IRREDUCIBLE witnesses
--                              after this demotion — the other 4
--                              elements are derived)
--
--   28 · 6 = 168 ✓
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.F2.HodgeDim3.MetricGauge.StabiliserClosure where

open import Relation.Binary.PropositionalEquality
  using (_≡_; trans; cong)

open import Substrate.Algebra.F2.Linear
open import Substrate.Algebra.F2.HodgeDim3.MetricGauge
  using (metric-id; congruence-act)
open import Substrate.Algebra.F2.HodgeDim3.MetricGauge.Stabiliser
  using (s₁; s₂; s₁-stabilises-metric-id; s₂-stabilises-metric-id)
open import Substrate.Algebra.F2.HodgeDim3.MetricGauge.CongruenceBridge
  using (congruence-compose-3)
open import Substrate.Category.Coalgebra
  using (FixedPoint)

------------------------------------------------------------------------
-- N-1: s₁∘s₂-stabilises-metric-id — demoted to 3 lines.
--
-- Derivation via congruence-compose-3 + the two Coxeter generator
-- stabiliser witnesses:
--
--   congruence-act (s₁ ∘L s₂) metric-id
--     ≡ congruence-act s₂ (congruence-act s₁ metric-id)   [congruence-compose-3]
--     ≡ congruence-act s₂ metric-id                       [s₁-stabilises-metric-id]
--     ≡ metric-id                                          [s₂-stabilises-metric-id]
------------------------------------------------------------------------

s₁∘s₂-stabilises-metric-id :
  congruence-act (s₁ ∘L s₂) metric-id ≡ metric-id
s₁∘s₂-stabilises-metric-id =
  trans (congruence-compose-3 s₁ s₂ metric-id)
  (trans (cong (congruence-act s₂) s₁-stabilises-metric-id)
         s₂-stabilises-metric-id)

------------------------------------------------------------------------
-- N-2: Categorical retrofit — 3-cycle stabilisation as FixedPoint.
--
-- Per `feedback_categorical_name_first` and the
-- Substrate.Category.Primitives roadmap. (Retained from the prior
-- retrofit slice.)
------------------------------------------------------------------------

metric-id-fixed-by-cong-act-s₁∘s₂ :
  FixedPoint (congruence-act (s₁ ∘L s₂)) metric-id
metric-id-fixed-by-cong-act-s₁∘s₂ =
  record { fixed = s₁∘s₂-stabilises-metric-id }

------------------------------------------------------------------------
-- N-3: Capstone documentation.
--
-- The full 6-element S₃ stabiliser of metric-id under GL(3, F₂)
-- congruence:
--
--   e                     — identity
--   s₁                    — swap (0, 1)              [Stabiliser.agda]
--   s₂                    — swap (1, 2)              [Stabiliser.agda]
--   s₁ ∘L s₂              — 3-cycle (0 → 1 → 2)     [this file, demoted]
--   s₂ ∘L s₁              — 3-cycle (0 → 2 → 1)     [derivable, same template]
--   s₁ ∘L s₂ ∘L s₁ = s₂ ∘L s₁ ∘L s₂ — swap (0, 2)  [derivable, same template]
--
-- Coxeter presentation: ⟨ s₁, s₂ | s₁² = s₂² = (s₁s₂)³ = e ⟩.
--
-- The 2 Coxeter generators are the IRREDUCIBLE stabiliser witnesses
-- after this demotion — the remaining 4 elements are mechanical
-- corollaries via `congruence-compose-3`. Same derivation pattern
-- applied to (s₂, s₁), (s₁ ∘L s₂, s₁), and (s₂ ∘L s₁, s₂) gives the
-- other elements; deferred as a "stabiliser-closure-full" follow-on
-- slice (which would be ~12-15 lines total, replacing the 4 missing
-- per-cycle proofs).
--
-- Deferred coalgebraic-unfolding slices (now mechanical given
-- congruence-compose-3):
--
--   * **stabiliser-closure-full**: derive the remaining 3 stabiliser
--     elements (s₂∘L s₁, s₁∘L s₂∘L s₁, s₂∘L s₁∘L s₂). Closes the
--     full 6-element subgroup.
--
--   * **bridge-to-Substrate.Groups.S3**: formally connect this
--     concrete Linear 3 3 stabiliser to the existing S₃ group
--     structure.
------------------------------------------------------------------------
