------------------------------------------------------------------------
-- Substrate.Groups.Z3-Coxeter-via-Cyclic
--
-- Prototype of the Phase 4 migration: Z₃-Coxeter rebuilt on top of
-- Coxeter.Cyclic 2 with pattern synonyms for the named constructors.
--
-- The substrate currently has ~40+ pattern-matches on `Z₃.c-ε`,
-- `Z₃.c-a`, `Z₃.c-aa` across downstream files (Actions/S3-on-V4/*,
-- Z-x-FreeCyclic-PhaseAdvance, etc.). For a full migration to be
-- non-breaking, those patterns must continue to work.
--
-- Pattern synonyms in Agda let pattern-matching on `c-ε` resolve to
-- `(zero , c-here zero)` transparently. This file tests whether the
-- pattern synonyms approach is viable BEFORE committing to the full
-- in-place replacement of Z3-Coxeter.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Groups.Z3-Coxeter-via-Cyclic where

open import Substrate.Foundation.Fin using (Fin; zero; suc)
open import Substrate.Foundation.Product using (Σ; _,_)
import Substrate.Groups.Coxeter.Cyclic 2 as Cyc

------------------------------------------------------------------------
-- Re-export the cyclic structure publicly.
------------------------------------------------------------------------

open Cyc public using (Gen; a; power; insert; σ; σ-HasOrderPerm)

open import Substrate.Groups.Coxeter.Word using (Word; []; _∷_)

------------------------------------------------------------------------
-- Z₃'s Canonical = existential view of Cyclic 2's Canonical.
------------------------------------------------------------------------

Canonical : Word Gen → Set
Canonical w = Σ (Fin 3) (Cyc.Canonical w)

------------------------------------------------------------------------
-- Named-constructor pattern synonyms.
--
-- These let downstream pattern-matches like `f Z₃.c-ε = ...` continue
-- to work transparently, while the underlying Canonical is the
-- length-indexed existential.
------------------------------------------------------------------------

pattern c-ε  = zero               , Cyc.c-here zero
pattern c-a  = suc zero           , Cyc.c-here (suc zero)
pattern c-aa = suc (suc zero)     , Cyc.c-here (suc (suc zero))

------------------------------------------------------------------------
-- Verify pattern synonyms work: define a function by case-split.
------------------------------------------------------------------------

private
  -- Test: count generators using the named constructors.
  count : ∀ {w} → Canonical w → Fin 3
  count c-ε  = zero
  count c-a  = suc zero
  count c-aa = suc (suc zero)
