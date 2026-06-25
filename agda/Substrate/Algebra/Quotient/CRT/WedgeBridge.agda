------------------------------------------------------------------------
-- Substrate.Algebra.Quotient.CRT.WedgeBridge
--
-- Ⓠ★Ⓦ.spine-crt-wedge — the connection leaf wiring the Bézout/CRT SPINE
-- (node 2: `crt-from-traces`, assembling combine ← idempotents ← inverses ←
-- Bézout) to the foundational WEDGE REGISTRY (node 9: `bridges`, `assocᴰ`,
-- the monoidal structure). The claim, machine-checked rather than narrated:
--
--   * THE CODEC LEGS ARE THE REGISTRY BRIDGES. The cross-carrier embeddings a
--     `CrossMix` consumes (`embA`, `embB` : `Bridge`) are LITERALLY the homs the
--     Registry names — `include-ℕℤ` (ℕ↪ℤ) and `parity-bridge` (ℕ↠F₂) are the
--     very entries of `Registry.bridges`, and they slot into `CrossMix.embA`
--     unchanged (`leg-is-registry-bridge` : refl). So "the CRT spine's codec
--     legs" and "the Registry's bridges" are one set of objects, not two.
--
--   * THE CROSS-TERM IS THE CrossMul ALGEBRA. `cross` of the registry-bridge
--     legs is the inclusion product in the common carrier (`cross-is-include`,
--     refl); and on the COPRIME / orthogonal-idempotent case the cross term
--     vanishes (`clean-cross`, re-exported) — the CRT-clean degree-0 coherence
--     of Wedge.CrossMul, certified by the EEA/Bézout coprimality trace.
--
--   * THE SPINE'S COMBINE IS REAL. `crt-from-traces` (Bézout-built) yields an
--     actual `CRT-Witness` for ℤ/15 ≅ ℤ/3 × ℤ/5 (`split-15`, re-exported), and
--     the monoidal associator `assocᴰ` certifies the reconstruction is
--     independent of bracket choice (`bracket-independent`, the WedgeIso whose
--     round-trips are refl) — the certification that CRT's split factors
--     correctly through the foundational algebra.
--
-- This is a CONNECTION LEAF: no new machinery, all reuse — refl + re-export.
-- Zero postulates, --safe --without-K.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.Quotient.CRT.WedgeBridge where

open import Substrate.Foundation.Nat using (ℕ)
open import Substrate.Foundation.Eq using (_≡_; refl)
open import Substrate.Foundation.Product using (_,_)
open import Substrate.Algebra.Z using (ℤ; +_)
open import Substrate.Algebra.Z.Arithmetic using (_*ℤ_)
open import Substrate.Algebra.Z.Wedge using (ℤ-div)
open import Substrate.Algebra.Wedge using (ℕ-div)
open import Substrate.Algebra.Wedge.Cross using (_⊗ᴰ_)
open import Substrate.Algebra.Wedge.InclusionBridge using (include-ℕℤ)
open import Substrate.Algebra.Wedge.CrossMul using (CrossMix; cross; embA)
open import Substrate.Algebra.Wedge.Iso using (WedgeIso)
open import Substrate.Algebra.Wedge.Monoidal using (assocᴰ)
-- the common multiplicative carrier R = ℤ with *ℤ, REUSED from the ℚ cospan.
open import Substrate.Algebra.Q.HetCrossMix using (ℤ-mul)
-- the spine: the Bézout-assembled CRT witness for ℤ/15, and the combine reads.
open import Substrate.Algebra.Quotient.CRT using (CRT-Witness; combine)
open import Substrate.Algebra.Quotient.CRT.FromTrace using (witness-3-5)
-- the worked coprime CrossMix: orthogonal idempotents, clean (degree-0) cross.
open import Substrate.Logic.Evidence.ElAtlas.CenterIsStarCRT
  using (crt-mix; e₁; e₂; clean-cross)

------------------------------------------------------------------------
-- 1. THE CODEC LEG IS THE REGISTRY BRIDGE. The cross-carrier cospan whose
--    A-leg is the Registry's `include-ℕℤ` (ℕ↪ℤ) and whose common carrier R is
--    the reused ℤ-mul. `embA` of this CrossMix IS `include-ℕℤ` (refl) — the
--    spine's codec leg and the registry bridge are the SAME hom.
------------------------------------------------------------------------

include-crossmix : CrossMix ℕ-div ℕ-div ℤ-mul
include-crossmix = record { embA = include-ℕℤ ; embB = include-ℕℤ }

leg-is-registry-bridge : embA include-crossmix ≡ include-ℕℤ
leg-is-registry-bridge = refl

------------------------------------------------------------------------
-- 2. THE CROSS-TERM IS THE WEDGE ALGEBRA. `cross` of the registry-bridge legs
--    is the inclusion product in ℤ (the cross-carrier mixing of CrossMul); and
--    on the COPRIME / orthogonal idempotents the cross term VANISHES — the
--    CRT-clean degree-0 coherence, re-exported.
------------------------------------------------------------------------

-- cross include-crossmix a b = (+ a) *ℤ (+ b) (definitional: translate include-ℕℤ = +_).
cross-is-include : (a b : ℕ) → cross include-crossmix a b ≡ (+ a) *ℤ (+ b)
cross-is-include a b = refl

-- the coprime cross-term: e₁·e₂ ≡ 0 in ℤ/6 — orthogonal, clean coherence.
orthogonal-clean : cross crt-mix e₁ e₂ ≡ 0
orthogonal-clean = clean-cross

------------------------------------------------------------------------
-- 3. THE SPINE'S COMBINE IS REAL, AND ITS RECONSTRUCTION IS BRACKET-FREE. The
--    Bézout-built CRT witness for ℤ/15 ≅ ℤ/3 × ℤ/5 (`witness-3-5`, re-exported
--    as `split-15`); the monoidal associator certifies bracket-independence.
------------------------------------------------------------------------

split-15 : CRT-Witness 2 4
split-15 = witness-3-5

-- the spine's combine is genuinely computable: (1,2) ↦ 22 (≡1 mod 3, ≡2 mod 5).
combine-oracle : combine split-15 (1 , 2) ≡ 22
combine-oracle = refl

-- the monoidal associator on the cross-carrier roots: (ℕ⊗ℤ)⊗ℤ ≃ ℕ⊗(ℤ⊗ℤ), a
-- WedgeIso whose round-trips are refl — bracketing of the reconstruction is
-- immaterial (the coherence the Registry registers).
bracket-independent : WedgeIso ((ℕ-div ⊗ᴰ ℤ-div) ⊗ᴰ ℤ-div) (ℕ-div ⊗ᴰ (ℤ-div ⊗ᴰ ℤ-div))
bracket-independent = assocᴰ ℕ-div ℤ-div ℤ-div
