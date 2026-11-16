------------------------------------------------------------------------
-- Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded.Coemitrung4genuineactioncomp
--
-- Defines: coemit-rung4-genuine-action-comp
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K --guardedness #-}

module Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded.Coemitrung4genuineactioncomp where

open import Substrate.Foundation.Nat.Nat
open import Substrate.Category.Allegory.Refinement.Preamble
open import Substrate.Foundation.Fin.Fin
open import Substrate.Foundation.Fin.Fin
open import Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded.GradingAxis
open import Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded.S3onaxis
open import Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded.S3actcomp
open import Substrate.Foundation.Eq
open import Substrate.Groups.SemidirectProduct.Stab   -- Stab X σ = applyₛ σ X ≡ X (σ FIXES X)
open import Substrate.Foundation.Eq.Cong
open import Substrate.Foundation.Eq.Sym
open import Substrate.Foundation.Eq.Trans


-- (3) coemit-rung4-genuine-action: the S₃-action on the 3 axes IS a genuine G-action (act-id + act-comp, 333), and
--     its carrier at rung 4 is the V₄ coset space (|V₄|=4). The action is genuine: identity acts trivially, and
--     composition composes (s3-act-id/s3-act-comp) — the G-action laws, now on the canonical V₄'s involutions.
-- (⟡coemit-dedup-s3-act-id, DISCHARGED) A duplicate of `s3-act-id` lived here as `coemit-rung4-genuine-action-id`,
-- a bare alias with no downstream uses. Removed: shared structure should be REFERENCED, not restated
-- (D-decompose-not-dedup-clean; the 299 meta-frame — duplication is under-decomposition, not health).
-- Found by a hand-rolled vacuity scan; kept here as the RESIDUE of that finding (shadow, not deletion).

coemit-rung4-genuine-action-comp : (σ τ : Fin 3 → Fin 3) (a : GradingAxis)
                                 → s3-on-axis σ (s3-on-axis τ a) ≡ s3-on-axis (λ x → σ (τ x)) a
coemit-rung4-genuine-action-comp = s3-act-comp
