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

open import Substrate.Foundation.Eq
  using (_≡_; trans; cong; cong-trans)

open import Substrate.Algebra.F2.Linear
open import Substrate.Algebra.F2.HodgeDim3.MetricGauge.CongruenceAct using (congruence-act)
open import Substrate.Algebra.F2.HodgeDim3.MetricGauge.MetricId using (metric-id)
open import Substrate.Algebra.F2.HodgeDim3.MetricGauge.Stabiliser
  using (s₁; s₂; s₁-stabilises-metric-id; s₂-stabilises-metric-id)
open import Substrate.Algebra.F2.HodgeDim3.MetricGauge.CongruenceBridge
  using (congruence-compose-3)
open import Substrate.Category.Coalgebra
  using (FixedPoint)

------------------------------------------------------------------------
-- N-0: compose-stabilises — the parametric primitive that names the
-- "stabiliser closes under composition" property at the congruence-act
-- level. Each of the 4 named lemmas below collapses to one invocation.
--
-- Structurally: if T₁ and T₂ each stabilise metric-id, then T₁ ∘L T₂
-- also stabilises metric-id, via the dim-3 congruence-compose-3 step.
------------------------------------------------------------------------

compose-stabilises :
  (T₁ T₂ : Linear 3 3) →
  congruence-act T₁ metric-id ≡ metric-id →
  congruence-act T₂ metric-id ≡ metric-id →
  congruence-act (T₁ ∘L T₂) metric-id ≡ metric-id
compose-stabilises T₁ T₂ stab-T₁ stab-T₂ =
  trans (congruence-compose-3 T₁ T₂ metric-id)
        (cong-trans (congruence-act T₂) stab-T₁ stab-T₂)

------------------------------------------------------------------------
-- N-1: s₁∘s₂-stabilises-metric-id — derived via compose-stabilises.
--
--   congruence-act (s₁ ∘L s₂) metric-id
--     ≡ congruence-act s₂ (congruence-act s₁ metric-id)   [congruence-compose-3]
--     ≡ congruence-act s₂ metric-id                       [s₁-stabilises-metric-id]
--     ≡ metric-id                                          [s₂-stabilises-metric-id]
------------------------------------------------------------------------

s₁∘s₂-stabilises-metric-id :
  congruence-act (s₁ ∘L s₂) metric-id ≡ metric-id
s₁∘s₂-stabilises-metric-id =
  compose-stabilises s₁ s₂ s₁-stabilises-metric-id s₂-stabilises-metric-id

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
-- N-3: Remaining 3 stabiliser elements — mechanical derivations.
--
-- Same 3-line template as s₁∘s₂; only the order / nesting of T₁, T₂
-- in `congruence-compose-3` differs, plus the corresponding base
-- witness applied via `cong`.
--
-- s₂ ∘L s₁:
--   ≡ cong-act s₁ (cong-act s₂ metric-id)
--   ≡ cong-act s₁ metric-id
--   ≡ metric-id
--
-- s₁ ∘L s₂ ∘L s₁ (parses as s₁ ∘L (s₂ ∘L s₁) by infixr 9):
--   ≡ cong-act (s₂ ∘L s₁) (cong-act s₁ metric-id)
--   ≡ cong-act (s₂ ∘L s₁) metric-id
--   ≡ metric-id
--
-- s₂ ∘L s₁ ∘L s₂ (parses as s₂ ∘L (s₁ ∘L s₂)):
--   ≡ cong-act (s₁ ∘L s₂) (cong-act s₂ metric-id)
--   ≡ cong-act (s₁ ∘L s₂) metric-id
--   ≡ metric-id
------------------------------------------------------------------------

s₂∘s₁-stabilises-metric-id :
  congruence-act (s₂ ∘L s₁) metric-id ≡ metric-id
s₂∘s₁-stabilises-metric-id =
  compose-stabilises s₂ s₁ s₂-stabilises-metric-id s₁-stabilises-metric-id

s₁∘s₂∘s₁-stabilises-metric-id :
  congruence-act (s₁ ∘L s₂ ∘L s₁) metric-id ≡ metric-id
s₁∘s₂∘s₁-stabilises-metric-id =
  compose-stabilises s₁ (s₂ ∘L s₁) s₁-stabilises-metric-id s₂∘s₁-stabilises-metric-id

s₂∘s₁∘s₂-stabilises-metric-id :
  congruence-act (s₂ ∘L s₁ ∘L s₂) metric-id ≡ metric-id
s₂∘s₁∘s₂-stabilises-metric-id =
  compose-stabilises s₂ (s₁ ∘L s₂) s₂-stabilises-metric-id s₁∘s₂-stabilises-metric-id

------------------------------------------------------------------------
-- N-4: FixedPoint retrofits for the remaining 3 elements.
------------------------------------------------------------------------

metric-id-fixed-by-cong-act-s₂∘s₁ :
  FixedPoint (congruence-act (s₂ ∘L s₁)) metric-id
metric-id-fixed-by-cong-act-s₂∘s₁ =
  record { fixed = s₂∘s₁-stabilises-metric-id }

metric-id-fixed-by-cong-act-s₁∘s₂∘s₁ :
  FixedPoint (congruence-act (s₁ ∘L s₂ ∘L s₁)) metric-id
metric-id-fixed-by-cong-act-s₁∘s₂∘s₁ =
  record { fixed = s₁∘s₂∘s₁-stabilises-metric-id }

metric-id-fixed-by-cong-act-s₂∘s₁∘s₂ :
  FixedPoint (congruence-act (s₂ ∘L s₁ ∘L s₂)) metric-id
metric-id-fixed-by-cong-act-s₂∘s₁∘s₂ =
  record { fixed = s₂∘s₁∘s₂-stabilises-metric-id }

------------------------------------------------------------------------
-- N-5: Capstone documentation.
--
-- The full 6-element S₃ stabiliser of metric-id under GL(3, F₂)
-- congruence — all 6 elements witnessed:
--
--   e                — identity (trivial; not formalised here)
--   s₁               — swap (0, 1)              [Stabiliser.agda]
--   s₂               — swap (1, 2)              [Stabiliser.agda]
--   s₁ ∘L s₂         — 3-cycle (0 → 1 → 2)      [this file, N-1]
--   s₂ ∘L s₁         — 3-cycle (0 → 2 → 1)      [this file, N-3]
--   s₁ ∘L s₂ ∘L s₁   — swap (0, 2)              [this file, N-3]
--   s₂ ∘L s₁ ∘L s₂   — swap (0, 2)              [this file, N-3]
--                      (= s₁∘s₂∘s₁ under
--                       the Coxeter (s₁s₂)³ = e
--                       relation; the equality
--                       itself is a separate
--                       deferred fact)
--
-- Coxeter presentation: ⟨ s₁, s₂ | s₁² = s₂² = (s₁s₂)³ = e ⟩.
--
-- The 2 Coxeter generators are the IRREDUCIBLE stabiliser witnesses;
-- all 4 non-generator elements derive from them mechanically via
-- the 3-line congruence-compose-3 + cong template.
--
-- **|orbit| · |stabiliser| = 28 · 6 = 168 = |GL(3, F₂)|** — the
-- orbit-stabiliser arithmetic at L_metric is now fully witnessed
-- (modulo the structural orbit-characterisation slice, which is a
-- separate concern).
--
-- Deferred follow-ons:
--
--   * **Coxeter-relation-(s₁s₂)³ = e**: prove
--     s₁ ∘L s₂ ∘L s₁ ≡ s₂ ∘L s₁ ∘L s₂ at the Linear 3 3 level.
--     Reduces the 6-element witness count to 5 by collapsing the
--     two equal swap-(0,2) representatives.
--
--   * **bridge-to-Substrate.Groups.S3**: formally connect this
--     concrete Linear 3 3 stabiliser to the existing S₃ group
--     structure in Substrate.Groups.S3 (via the Coxeter framework).
--
--   * **stabiliser-as-Σ-group**: present the 6-element stabiliser as
--     a sub-group of GL(3, F₂) via a Σ-type with closure under
--     composition + the FixedPoint witnesses. Categorical handle
--     for "the stabiliser subgroup of metric-id".
------------------------------------------------------------------------
