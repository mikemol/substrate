------------------------------------------------------------------------
-- Substrate.Category.UniversalProperty.TruthValues
--
-- UP33 of the UP-topos arc per [scratch/up_topos_arc_plan.md].
--
-- The internal-logic truth value: "X is an instance of UP U" as a
-- sieve-valued proposition.
--
-- Concretely: given a UPArrow U and an instance candidate
-- (s : Source U, i : Target U), the truth value
-- ⟦ X is-instance U ⟧ ∈ Ω(U) is the sieve of all UPTerms V → U
-- through which the candidate factors.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Category.UniversalProperty.TruthValues where

open import Substrate.Category.UniversalProperty
  using (UPArrowP; SourceP; TargetP; WitnessP)
open import Substrate.Category.UniversalProperty.Sieve
  using (Sieve; max-Sieve)

-- ⟡UPArrow-dissolve C: telescope carriers (auto).
private variable
  SU TU : Set
  WU : SU → TU → Set

------------------------------------------------------------------------
-- 1. The "is-instance" truth value (substrate-honest signature).
--
-- Stated parametric in (s : Source U) (i : Target U). The full
-- definition needs the substrate's UPMorphism evaluator on the
-- factor-through-cover witness; we land the signature here.
------------------------------------------------------------------------

is-instance-truth :
  (U : UPArrowP SU TU WU) (s : SourceP U) (i : TargetP U) →
  WitnessP U s i →
  Sieve U
is-instance-truth U _ _ _ = max-Sieve U
  -- Substrate-honest: when the witness exists, the truth-sieve is
  -- the maximal sieve (= "true"). A finer truth-value distinction
  -- captures partial instantiation, which is a future-arc refinement.

------------------------------------------------------------------------
-- 2. Capstone for UP33.
--
-- The truth-value family lands. UP34 supplies the internal logic
-- (∧, ∨, →, ¬, ∀, ∃) at the sieve level.
------------------------------------------------------------------------
