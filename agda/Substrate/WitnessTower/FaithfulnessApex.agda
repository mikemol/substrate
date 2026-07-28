------------------------------------------------------------------------
-- Substrate.WitnessTower.FaithfulnessApex
--
-- ⟡faithfulness-apex — the TRUE APEX of the faithfulness sites. This
-- session co-apexed several "determined by its action" witnesses
-- (FaithfulnessBridge: SnGroup.apply-injective, Symmetric._≈_, extract-s,
-- row-inj). The graded-wedge study revealed their common apex:
-- AxisWord.Detector's OBLIGATION A2 — the DETECTOR GRADE, `detect a b ≡ 𝟘 ⟺
-- a ≡ b` (kernel = the diagonal = non-distinctions). The exterior `a ∧ a = 0`
-- IS this detector reading; permutation faithfulness is the SAME structure at
-- the Perm carrier.
--
-- This file connects them: instantiate Detector at Perm n (decidable eq from
-- Fin ≟ via Vec ≡-dec), then show the tower's permutation faithfulness
-- (apply-injective: pointwise action-agreement ⟹ σ ≡ τ) IS the detector's
-- kernel law (detect σ τ ≡ 𝟘 ⟹ σ ≡ τ) composed with the action reading. So
-- "a permutation is determined by its action" and "the detector annihilates
-- nothing distinct" are ONE fact at Perm.
--
-- --safe --without-K. Verified on Agda 2.8.0.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.WitnessTower.FaithfulnessApex where

open import Substrate.Foundation.Nat using (ℕ)
open import Substrate.Foundation.Fin.Fin
open import Substrate.Foundation.Fin.Op
open import Substrate.Foundation.Vec using (Vec)
open import Substrate.Foundation.Vec.Properties using (≡-dec)
open import Substrate.Foundation.Eq using (_≡_; refl; trans; sym)
open import Substrate.Algebra.F2 using (F₂; 𝟘)

open import Substrate.WitnessTower.Enumerate using (Perm)
open import Substrate.WitnessTower.SnGroup using (apply; apply-injective)
import Substrate.Algebra.Wedge.AxisWord.Detector as Det

------------------------------------------------------------------------
-- 1. Perm n has decidable equality (Perm n = Vec (Fin n) n, from Fin ≟).
------------------------------------------------------------------------

_≟P_ : {n : ℕ} (σ τ : Perm n) → _
_≟P_ {n} = ≡-dec _≟_

------------------------------------------------------------------------
-- 2. Instantiate the detector grade at Perm n.
------------------------------------------------------------------------

module PermDetector {n : ℕ} = Det.Detector {Perm n} (_≟P_ {n})

-- The detector on permutations: detect σ τ = 𝟘 iff σ ≡ τ.
detectP : {n : ℕ} → Perm n → Perm n → F₂
detectP {n} = PermDetector.detect {n}

------------------------------------------------------------------------
-- 3. THE APEX CONNECTION. apply-injective (tower faithfulness, all rungs)
-- feeds the detector kernel: if the detector reads 𝟘 (no distinction), the
-- permutations are equal; conversely, pointwise action-agreement (the
-- Symmetric-≈ / FaithfulnessBridge hypothesis) yields σ ≡ τ hence detect 𝟘.
------------------------------------------------------------------------

-- detector kernel ⟹ equal (from Detector.detect-kernel).
apex-kernel : {n : ℕ} {σ τ : Perm n} → detectP σ τ ≡ 𝟘 → σ ≡ τ
apex-kernel {n} = PermDetector.detect-kernel {n}

-- action-agreement ⟹ detector reads no distinction. This is the payoff:
-- the FaithfulnessBridge hypothesis (∀ i → apply σ i ≡ apply τ i) — the
-- Symmetric-≈ / apply-injective input — lands at detector 𝟘. So permutation
-- faithfulness IS the detector grade's non-distinction reading.
action-agreement→detect-𝟘 :
  {n : ℕ} {σ τ : Perm n} →
  ((i : Fin n) → apply σ i ≡ apply τ i) → detectP σ τ ≡ 𝟘
action-agreement→detect-𝟘 {n} {σ} {τ} h =
  detect-eq→𝟘 (apply-injective h)
  where
    open PermDetector {n}
    -- detect a a = 𝟘 (detect-refl), transported along σ ≡ τ.
    detect-eq→𝟘 : σ ≡ τ → detectP σ τ ≡ 𝟘
    detect-eq→𝟘 refl = detect-refl σ
