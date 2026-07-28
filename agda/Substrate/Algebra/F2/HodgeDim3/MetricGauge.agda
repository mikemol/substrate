------------------------------------------------------------------------
-- Substrate.Algebra.F2.HodgeDim3.MetricGauge
--
-- M-11.metric-gauge slice. The 28-element metric gauge over F₂³:
-- non-degenerate symmetric bilinear forms, the GL(3, F₂) congruence
-- action, and ONE concrete transitivity witness. File-per-lemma:
--
--   MetricGauge.Type                 — SymBilinForm-3 + 6 accessors
--   MetricGauge.Det                  — det-sym3
--   MetricGauge.NonDegenerate        — predicate det m ≡ 𝟙
--   MetricGauge.MetricId             — diagonal identity exemplar
--   MetricGauge.MetricMixed          — one-coupling exemplar
--   MetricGauge.MetricFullyCoupled   — fully-coupled exemplar
--   MetricGauge.BilinearFormOf       — v^T M w
--   MetricGauge.CongruenceAct        — T^T M T action
--   MetricGauge.TIdToMixed           — concrete T : id → mixed
--   MetricGauge.CongruenceIdToMixed  — orbit transitivity witness
--
-- The metric is the "discrete Hodge ★" parameter at n=3 — different
-- metrics give different orthogonality structures on F₂³ and hence
-- different self-dual subspaces. The 28 non-degenerate forms form a
-- SINGLE GL(3, F₂) orbit (= gauge), so any choice is structurally
-- equivalent under the GL(3, F₂) symmetry.
--
-- Per `feedback_expose_generator_not_orbit` + `feedback_coalgebraic_
-- not_consumer_driven`: this slice exposes the gauge via the inference
-- rule (`NonDegenerate` predicate = `det ≡ 𝟙`) and the generator
-- (GL(3, F₂) congruence action), NOT via enumeration. The cardinality
-- 28 = 168/6 is a derived orbit-stabiliser consequence.
--
-- The 3 exemplar metrics witness distinct shape-classes under the S₃
-- axis-permutation subgroup of GL(3, F₂); under the full GL(3, F₂)
-- they're all gauge-equivalent in the same 28-element orbit.
--
-- Class sizes (verified by hand-count):
--   1 diagonal + 9 one-interaction + 15 two-interaction + 3 fully-coupled = 28.
--
-- Follow-on coalgebraic-unfolding slices: see M-11.metric-gauge.DBE.md.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.F2.HodgeDim3.MetricGauge where

open import Substrate.Algebra.F2.HodgeDim3.MetricGauge.Type
open import Substrate.Algebra.F2.HodgeDim3.MetricGauge.Det
open import Substrate.Algebra.F2.HodgeDim3.MetricGauge.NonDegenerate
open import Substrate.Algebra.F2.HodgeDim3.MetricGauge.MetricId
open import Substrate.Algebra.F2.HodgeDim3.MetricGauge.MetricMixed
open import Substrate.Algebra.F2.HodgeDim3.MetricGauge.MetricFullyCoupled
open import Substrate.Algebra.F2.HodgeDim3.MetricGauge.BilinearFormOf
open import Substrate.Algebra.F2.HodgeDim3.MetricGauge.CongruenceAct
open import Substrate.Algebra.F2.HodgeDim3.MetricGauge.TIdToMixed
open import Substrate.Algebra.F2.HodgeDim3.MetricGauge.CongruenceIdToMixed