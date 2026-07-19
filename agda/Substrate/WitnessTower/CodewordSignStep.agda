------------------------------------------------------------------------
-- Substrate.WitnessTower.CodewordSignStep
--
-- ⟡codeword-step (HONESTLY SCOPED). The catalog's CY-5 "codeword" is a
-- FIXED-cardinality ambient: Codeword = Bool⁵ (32 = 24 live + 8 reserved),
-- with NO grade/recon structure of its own (checked: no codeword file carries
-- a grade, step, or insert-at). So "lift each of the 5 bits to a graded
-- respects-recon family" would be a FABRICATION — four of the bits are
-- grade-0 fixed data:
--   b₀ b₁ = axis (D/C/S/W, the 4 V₄ axes)   — fixed, not grade-raising
--   b₃ b₄ = reserved/live selector          — fixed cardinality split
--   b₂    = sign (reserved) / ordering (live) — the ONE bit with ℤ/2 content
--
-- The genuine grade-varying content is the SIGN bit b₂. Per WHTCharacterBridge
-- the live codeword's selector reads the same ℤ/2 as the tower's permutation
-- sign (bool→F₂ ∘ sign). And the codeword's live 24 ARE S₄ = Perm 4 = rung 3
-- of the tower (Codeword.LiveS4: live-to-permutation).
--
-- HONEST STATUS. What this file DOES establish: the step law sign-step at the
-- grade that builds S₄ (insert-at : Fin 4 → Perm 3 → Perm 4 = the witnessing
-- step INTO rung 3), so the sign of any rung-3 permutation obeys the step law.
-- The codeword's live 24 INHABIT this grade (live-to-permutation : Live → S₄).
--
-- The codeword-sign ↔ permutation-sign tie is now DISCHARGED — but NOT as the
-- assumption "b₂ = sign". Computing the grid (WitnessTower.CodewordSign
-- EqualsStabParity) showed b₂ ≠ sign in general; the true theorem is
--   codeword-sign a sel ≡ stab-parity sel   (axis-independent = V₄ ⊂ A₄)
-- i.e. the live codeword's sign is the S₃-STABILISER PARITY, not the ordering
-- selector b₂. See CodewordSignEqualsStabParity for the 24-case proof and
-- WitnessTower.SignStabTotal for the general (all-of-S₄) orientation-anchored
-- form sign σ = sign(s-for σ). This file records the grade-3 step INSTANCE the
-- codeword connects through; the sign-value theorem lives in those two files.
--
-- --safe --without-K. Verified on Agda 2.8.0.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.WitnessTower.CodewordSignStep where

open import Substrate.Foundation.Nat using (ℕ; suc)
open import Substrate.Foundation.Fin using (Fin; zero; suc)
open import Substrate.Foundation.Vec using (Vec; map)
open import Substrate.Foundation.Bool using (Bool; _xor_)
open import Substrate.Foundation.Eq using (_≡_)
open import Substrate.Foundation.Fin.Punctured using (punchIn)

open import Substrate.WitnessTower.Enumerate using (Perm; insert-at)
open import Substrate.WitnessTower.Wedge.OrientationRigCatPermSign using (sign; parityLess)
open import Substrate.WitnessTower.SignStepCocycle using (sign-step)

------------------------------------------------------------------------
-- The codeword lives at rung 3 (S₄ = Perm 4). Rung 3 is reached from rung 2
-- (Perm 3) by ONE witnessing insertion insert-at p : Perm 3 → Perm 4. The
-- sign of that rung-3 codeword-permutation is governed by the step law at
-- n = 3 — the grade-3 instance of the general step-wise sign correspondence.
------------------------------------------------------------------------

-- The codeword-sign step: sign of a rung-3 permutation (= a live codeword,
-- via LiveS4.live-to-permutation) built by inserting top digit p over a
-- rung-2 base σ. This is sign-step specialised to the step INTO S₄.
codeword-sign-step :
  (p : Fin 4) (σ : Perm 3) →
  sign (insert-at p σ) ≡ (parityLess p (map (punchIn p) σ) xor sign σ)
codeword-sign-step p σ = sign-step p σ

-- (Honest: the OTHER codeword bits — axis b₀b₁, selector b₃b₄ — are grade-0
-- fixed data with no step law; there is nothing to lift for them. The sign
-- bit b₂ is the sole grade-varying content, and this is its step instance.)
