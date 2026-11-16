------------------------------------------------------------------------
-- Substrate.Groups.V4-Normality
--
-- V_4 ⊳ S_4 — the V_4 image inside S_4 is a normal subgroup.
--
-- `V₄-normal` is a thin delegating definition (see the `public`-retired note
-- below for why this module no longer re-exports its imports): the proof is structural:
-- V_4 is the N-component of S_4 ≅ V_4 ⋊ S_3, and so its normality in
-- S_4 is licensed by the SP combinator's `N-normal-in-SP` in
-- Substrate.Groups.Coxeter.SemidirectProductGroup, transported through
-- the iso S_4-Composed ≅ Permutation Axis in Substrate.Groups.S4-Iso.
--
-- Previous history: this module formerly carried a predicate-based
-- classification (is-V₄-shape + 4-product + per-axis case analysis,
-- ~427 lines). That proof has been retired in favour of the structural
-- compositional proof. The proof is now an iso-transport composed
-- entirely of:
--
--   * H-2 perm-roundtrip-≈            (S4-Iso)
--   * H-4 embed-as-N-injection        (S4-Iso)
--   * forward-hom + forward-ε + K-2 forward-inv (S4-Iso)
--   * H-3 N-normal-in-SP              (SemidirectProductGroup)
--
-- See: catalog/cocycles.md § CY-5 V_4 ⋊ S_3 ≅ S_4;
--      Substrate.Groups.V4-Embedding (S8) — the gap this closes.
--      [[feedback-v4-typeclass-architecture]],
--      [[feedback-composable-primitives-over-flat-enumeration]] —
--      the design rationale behind retiring the predicate proof.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Groups.V4-Normality where

-- ⚑ `public` RETIRED (Ⓑ2c).  Sole consumer `Groups.Subgroup` now binds
-- `S4-Iso` itself.  Both modules are blocked behind unrelated failures
-- (`S4-Iso`, `Symmetric.Permutation`), so this is verified by inspection of the
-- edge census rather than by a green compile — stated, not implied.
open import Substrate.Groups.S4-Iso using (V₄-normal-compositional)

-- V₄-normal: V₄ image is closed under conjugation by any S₄ element.
-- Defined as the structural-compositional construction; the predicate-
-- based proof (formerly inlined here) has been retired.
open import Substrate.Groups.V4-Embedding using (V₄-image)
open import Substrate.Axes.Axis using (Axis)
open import Substrate.Groups.Symmetric.Permutation Axis
open import Substrate.Groups.Symmetric.Permutation.Compose Axis using (_·_)
open import Substrate.Groups.Symmetric.Permutation.Inverse Axis using (_⁻¹)
open import Substrate.Groups.V4.Bijection.V4
open import Substrate.Groups.V4-Embedding using (embed)
open import Substrate.Groups.S4-Iso.V4Normal

V₄-normal :
  (σ : Permutation) (v : V₄) → V₄-image ((σ · embed v) · (σ ⁻¹))
V₄-normal = V₄-normal-compositional
