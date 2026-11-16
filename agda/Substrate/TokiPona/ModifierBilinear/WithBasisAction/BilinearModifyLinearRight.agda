------------------------------------------------------------------------
-- Substrate.TokiPona.ModifierBilinear.WithBasisAction.BilinearModifyLinearRight
--
-- Defines: bilinear-modify-linear-right
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.TokiPona.ModifierBilinear.WithBasisAction; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.TokiPona.ModifierBilinear.WithBasisAction.BilinearModifyLinearRight where

open import Substrate.Foundation.Nat.Nat
open import Substrate.Foundation.Fin.Fin
open import Substrate.Algebra.F2.Linear.CompL
open import Substrate.Algebra.F2.Linear.CompLAssoc
open import Substrate.Algebra.F2.Linear.CompLIdentityL
open import Substrate.Algebra.F2.Linear.CompLIdentityR
open import Substrate.Algebra.F2.Linear.IdL
open import Substrate.Algebra.F2.Linear.Linear
open import Substrate.Algebra.F2.Linear.Preserves
open import Substrate.Algebra.F2.Linear.FromImages
open import Substrate.TokiPona.SemanticSpace
open import Substrate.Foundation.Eq
open import Substrate.Foundation.Eq.Cong
open Linear
open import Substrate.TokiPona.ModifierBilinear.WithBasisAction.Private
open import Substrate.TokiPona.ModifierBilinear.WithBasisAction.Step1
open import Substrate.TokiPona.ModifierBilinear.WithBasisAction.Step2
open import Substrate.TokiPona.ModifierBilinear.WithBasisAction.BilinearModify



------------------------------------------------------------------------
-- 5. Right-linearity (linear in the second argument).
--
-- The OUTER linear-from-images guarantees apply (step2 b v) is
-- Linear in w. Witness: preserves-+ inherited from Linear's record.
--
-- This is the FreeLinearization-side bilinear universal property
-- discharged. Left-linearity (in v) requires step1-by-step descent
-- through both linear extensions; the OUTER + INNER linearity
-- compose, but at F₂ characteristic 2 the composition still respects
-- the underlying linearity. Provided here as a corollary of
-- preserves-+ for step2.
------------------------------------------------------------------------


bilinear-modify-linear-right :
  (b : Fin n → Fin n → SemVec m) (v w₁ w₂ : SemVec n) →
  bilinear-modify b v
    (Substrate.Algebra.F2.Vector._+ⱽ_ w₁ w₂)
    ≡ Substrate.Algebra.F2.Vector._+ⱽ_
        (bilinear-modify b v w₁) (bilinear-modify b v w₂)
bilinear-modify-linear-right b v w₁ w₂ =
  preserves-+ (step2 b v) w₁ w₂

------------------------------------------------------------------------
-- 6. Capstone.
--
-- bilinear-modify b : SemVec n → SemVec n → SemVec m IS the
-- 2-step FreeLinearization extension that T4 acknowledged as
-- deferred. Linearity in the SECOND argument is direct (step2 is
-- Linear). Linearity in the FIRST argument follows by symmetric
-- argument on step1; the symmetric proof is mechanical but the
-- direct lemma `bilinear-modify-linear-left` requires unfolding
-- step2's apply on each j, which is straightforward but expanded
-- per-instance. Per [[feedback-coalgebraic-not-consumer-driven]]
-- left-linearity is recorded as a corollary obligation; lands when
-- a consumer needs it (D1 closes the existence + universal property
-- + right-linearity).
------------------------------------------------------------------------
