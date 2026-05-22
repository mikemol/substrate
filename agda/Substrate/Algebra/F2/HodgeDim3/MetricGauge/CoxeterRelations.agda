------------------------------------------------------------------------
-- Substrate.Algebra.F2.HodgeDim3.MetricGauge.CoxeterRelations
--
-- The Coxeter relations for the S₃ presentation ⟨ s₁, s₂ |
-- s₁² = s₂² = (s₁s₂)³ = e ⟩ verified at the Linear 3 3 representation,
-- plus HasOrder retrofits. File-per-lemma:
--
--   S1SquaredOnE0/1/2/V  — s₁ ∘L s₁ ≡ id pointwise
--   S2SquaredOnE0/1/2/V  — s₂ ∘L s₂ ≡ id pointwise
--   BraidOnE0/1/2/V      — s₁s₂s₁ ≡ s₂s₁s₂ pointwise
--   S1Endo / S2Endo      — endomap wrappers
--   S1S2Endo             — endomap wrapper for s₁ ∘L s₂
--   HasOrderS1 / HasOrderS2 — Coxeter involutions retrofitted
--   S1S2CubedOnE0/1/2    — (s₁s₂)³ ≡ id per basis vector
--   HasOrderS1S2         — HasOrder s₁∘s₂-endo 3 (the 3-cycle)
--
-- All relations are pointwise apply-equalities (linear-extensionality);
-- full Linear-equality would need function-extensionality, which the
-- substrate avoids.
--
-- The braid relation `s₁ ∘L s₂ ∘L s₁ ≡ s₂ ∘L s₁ ∘L s₂` is the
-- structural identification of the two "swap-(0, 2)" representatives
-- in StabiliserClosure's witness list — after this slice the witness
-- count collapses from 6 (with two equal) to 5 distinct, matching
-- |S₃| - 1.
--
-- Per `feedback_v4_typeclass_architecture`: small finitely-presented
-- groups go through the Coxeter framework. Verifying the relations at
-- the Linear representation is the bridge from concrete-representation
-- to abstract-presentation. Per `project_torsion_element_universal`:
-- the s₁²/s₂² involutions and the (s₁s₂)³ = e braid are concrete
-- instances of the substrate's torsion-element-of-automorphism
-- universal, named here as HasOrder retrofits.
--
-- Deferred follow-ons:
--   * **Linear-equality version**: lifting `_-on-v` lemmas to
--     `s₁ ∘L s₁ ≡ id-L` etc. requires funext; substrate avoids it.
--   * **bridge-to-Substrate.Groups.S3**: connect this concrete
--     verification to the abstract S₃ presented in the Coxeter
--     framework.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.F2.HodgeDim3.MetricGauge.CoxeterRelations where

open import Substrate.Algebra.F2.HodgeDim3.MetricGauge.CoxeterRelations.S1SquaredOnE0  public
open import Substrate.Algebra.F2.HodgeDim3.MetricGauge.CoxeterRelations.S1SquaredOnE1  public
open import Substrate.Algebra.F2.HodgeDim3.MetricGauge.CoxeterRelations.S1SquaredOnE2  public
open import Substrate.Algebra.F2.HodgeDim3.MetricGauge.CoxeterRelations.S1SquaredOnV   public
open import Substrate.Algebra.F2.HodgeDim3.MetricGauge.CoxeterRelations.S2SquaredOnE0  public
open import Substrate.Algebra.F2.HodgeDim3.MetricGauge.CoxeterRelations.S2SquaredOnE1  public
open import Substrate.Algebra.F2.HodgeDim3.MetricGauge.CoxeterRelations.S2SquaredOnE2  public
open import Substrate.Algebra.F2.HodgeDim3.MetricGauge.CoxeterRelations.S2SquaredOnV   public
open import Substrate.Algebra.F2.HodgeDim3.MetricGauge.CoxeterRelations.BraidOnE0      public
open import Substrate.Algebra.F2.HodgeDim3.MetricGauge.CoxeterRelations.BraidOnE1      public
open import Substrate.Algebra.F2.HodgeDim3.MetricGauge.CoxeterRelations.BraidOnE2      public
open import Substrate.Algebra.F2.HodgeDim3.MetricGauge.CoxeterRelations.BraidOnV       public
open import Substrate.Algebra.F2.HodgeDim3.MetricGauge.CoxeterRelations.S1Endo         public
open import Substrate.Algebra.F2.HodgeDim3.MetricGauge.CoxeterRelations.S2Endo         public
open import Substrate.Algebra.F2.HodgeDim3.MetricGauge.CoxeterRelations.S1S2Endo       public
open import Substrate.Algebra.F2.HodgeDim3.MetricGauge.CoxeterRelations.HasOrderS1     public
open import Substrate.Algebra.F2.HodgeDim3.MetricGauge.CoxeterRelations.HasOrderS2     public
open import Substrate.Algebra.F2.HodgeDim3.MetricGauge.CoxeterRelations.S1S2CubedOnE0  public
open import Substrate.Algebra.F2.HodgeDim3.MetricGauge.CoxeterRelations.S1S2CubedOnE1  public
open import Substrate.Algebra.F2.HodgeDim3.MetricGauge.CoxeterRelations.S1S2CubedOnE2  public
open import Substrate.Algebra.F2.HodgeDim3.MetricGauge.CoxeterRelations.HasOrderS1S2   public
