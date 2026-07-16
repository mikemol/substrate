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

open import Substrate.Category.UniversalProperty.Sieve
  using (Sieve; max-Sieve)

module _ (O : Set) (Hom : O → O → Set) where

  ------------------------------------------------------------------------
  -- 1. The "is-instance" truth value (substrate-honest signature).
  --
  -- ⟡ta-upterm: objects are the Set₀ alphabet O; (O, Hom) via the section.
  -- ⟡TODO(ta-upterm): the old (s : SourceP U)(i : TargetP U) candidate +
  -- WitnessP U s i gate were object-INTERNAL plumbing over the old carrier-
  -- Set arrow; the O-form dissolves an object's Source/Target/Witness
  -- decomposition, so the parametric-candidate signature collapses to the
  -- bare object U. The truth-sieve is still the maximal sieve; a witness-
  -- gated / partial-instantiation refinement is a future-arc reintroduction
  -- (would re-thread a Hom-witness once the O-site names its candidate shape).
  ------------------------------------------------------------------------

  is-instance-truth : (U : O) → Sieve O Hom U
  is-instance-truth U = max-Sieve O Hom U
    -- Substrate-honest: the truth-sieve is the maximal sieve (= "true").

------------------------------------------------------------------------
-- 2. Capstone for UP33.
--
-- The truth-value family lands. UP34 supplies the internal logic
-- (∧, ∨, →, ¬, ∀, ∃) at the sieve level.
------------------------------------------------------------------------
