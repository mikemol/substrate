------------------------------------------------------------------------
-- Substrate.Category.BWTEmergence
--
-- Q9 of the codec arc: the empirical BWT-emergence finding lifted to
-- a substrate-level structural claim.
--
-- Empirical observation (from scratch/eliza's codec):
--   For a window of input bytes evaluated against all 16 nibble
--   rotations under full-speculation (each rotation's encoded cost
--   computed), the chosen rotations CONCENTRATE on a small set:
--   75% top-3 coverage at 256B / 32B-windows, weakening to 54% at
--   4096B.
--
-- This module formalises the structural shape: a RotationCommitMap
-- records the rotation chosen per window; the EmergentConcentration
-- predicate states "the image of this map factors through a small
-- subset of the rotation group."
--
-- Per [[bwt-emergence-conjecture]]:
--   Conjecture: every PrimeFactoredGauge with non-trivial rotation
--   action admits an EmergentConcentration witness when full-speculated.
--   The witness's bound depends on the input distribution; the
--   substrate-side claim is the STRUCTURAL existence of such a
--   factoring.
--
-- Per [[homology-cohomology-recursion]]:
--   observed = per-window rotation choices (homology)
--   catalogued = the small dominating subset (cohomology)
--   The catalogue's size measures the codec's gauge concentration.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Category.BWTEmergence where

open import Level using (Level; _⊔_) renaming (suc to lsuc)
open import Substrate.Foundation.Fin using (Fin)
open import Substrate.Foundation.Nat using (ℕ; zero; suc)
open import Substrate.Foundation.Product using (Σ; _,_)
open import Substrate.Foundation.Eq using (_≡_; refl)

------------------------------------------------------------------------
-- 1. RotationCommitMap — abstract per-window commit map.
--
-- For a stream of `n_windows` windows and a rotation group with
-- |Rotations| elements, a RotationCommitMap is a function assigning
-- a chosen rotation to each window.
------------------------------------------------------------------------

record RotationCommitMap
  (n_windows : ℕ) (n_rotations : ℕ) : Set where
  constructor mkRC
  field
    chosen : Fin n_windows → Fin n_rotations

open RotationCommitMap public

------------------------------------------------------------------------
-- 2. EmergentConcentration — the structural witness.
--
-- A RotationCommitMap exhibits EmergentConcentration with bound k iff
-- there exists a subset S ⊆ Rotations with |S| ≤ k such that every
-- chosen rotation lies in S.
--
-- The substrate-side BWT-emergence claim is the existence of such a
-- witness with k MUCH SMALLER than n_rotations. Empirically (from
-- the codec) k ≈ 3 covers 50-75% of windows; exact coverage depends
-- on input.
------------------------------------------------------------------------

-- A predicate "rotation r is in the subset S" parameterised by the
-- characteristic function `in-S : Fin n_rotations → Set`.

record EmergentConcentration
  {n_windows : ℕ} {n_rotations : ℕ}
  (rc : RotationCommitMap n_windows n_rotations)
  (k : ℕ)
  (in-S : Fin n_rotations → Set)
  : Set where
  constructor mkEmergent
  field
    -- All chosen rotations lie in S.
    all-in-S : (w : Fin n_windows) → in-S (chosen rc w)
    -- |S| ≤ k. (Existence of a size-bound witness; left abstract here.)
    bound : ℕ
    bound-le-k : bound ≡ k

open EmergentConcentration public

------------------------------------------------------------------------
-- 3. Connection to PrimeFactoredGauge.
--
-- The codec's full-speculation over nibble rotations is a CONCRETE
-- INSTANCE of this structure at:
--   n_rotations = 16 (nibble rotations)
--   n_windows = ⌈len(data) / window_size⌉
--   rc = the codec's argmin-over-cost rotation chooser
--   k = empirical bound (3 covers 75% at 256B / 32B-windows)
--
-- Instances of EmergentConcentration for the codec's specific
-- (n_windows, n_rotations, rc, k, in-S) tuple are constructed by
-- running the codec and observing the chosen-rotation histogram.
--
-- For larger PrimeFactoredGauge instances (e.g., GL(3, F₂) with 168
-- gauge elements, or the Monster with ~10⁵⁴), the same structural
-- claim applies in principle: full-speculation over the rotation
-- group produces a concentrated commit map. The empirical bound k
-- depends on input statistics; the structural existence is what this
-- module names.
------------------------------------------------------------------------

------------------------------------------------------------------------
-- 4. Cross-references.
--
-- * `ChainDecomposition` (Q8) — sibling primitive; chain factors
--   capture per-element decomposition, while RotationCommitMap
--   captures per-window rotation commitment.
-- * `SylowDecomposition` (T0) — both Q8 and Q9 operate over a
--   group with known Sylow structure.
-- * `PrimeFactoredGauge` (T1) — the universal-property gauge
--   space over which rotations act.
-- * `MultiRouteEquivariance` (T5) — the existence of a chain;
--   Q9's commit map is an empirically-concentrated CHOICE among
--   the chains.
-- * Codec runtime instance: `scratch/eliza/eliza/gpu_rotation_speculation.py`
--   `speculate_rotations_for_corpus` constructs a concrete
--   RotationCommitMap; `test_bwt_emergence.py` measures the
--   concentration bound.
------------------------------------------------------------------------
