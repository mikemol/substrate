------------------------------------------------------------------------
-- Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded.Coemits4isoshape
--
-- Defines: coemit-s4iso-shape
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K --guardedness #-}

module Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded.Coemits4isoshape where

open import Substrate.Foundation.Nat.Nat
open import Substrate.Algebra.R.Trace
open import Substrate.Category.UniversalProperty.ExtrudeCoEmitViaTrace.CoemitTrace
open import Substrate.Foundation.Product
open import Substrate.Category.Allegory.Refinement.Preamble
open import Substrate.Algebra.R.Trace.Bisim.Trans
open import Substrate.Category.UniversalProperty.ExtrudeBisimUpTo
open import Substrate.Algebra.R.Trace.Bisim.Refl
open import Substrate.Foundation.Fin.Fin
open import Substrate.Foundation.Fin.Fin
open import Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded.Anon
open import Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded.Anon2
open import Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded.GradingAxis
open import Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded.CoemitS4
open import Substrate.Foundation.Eq
open import Substrate.Groups.SemidirectProduct.Stab   -- Stab X σ = applyₛ σ X ≡ X (σ FIXES X)
open import Substrate.Foundation.Eq.Cong
open import Substrate.Foundation.Eq.Sym
open import Substrate.Foundation.Eq.Trans
open import Substrate.Category.Comonoid.Sites.V4
import Substrate.Algebra.R.Trace.V4FullCocycle as V4

-- (the two involutions are distinct: chirality lives on S₄/A₄ [group cosets]; dual-grade₃ on Λᵏ [Hodge grades].)

-- (4) coemit-s4iso-bridge: the canonical S₄ presentation is TotalSpace = Σ OrbitKey Fiber ≃ S₄ (6×4 = 24 = |S₃|·|V₄|)
--     — orbit_key = the Stab(D)-representative (6 = |S₃|), fiber = v4_delta ∈ V₄ (4 = |V₄|). coemit's CoemitS4 =
--     Σ GradingAxis (Fin 3 → Fin 3) has the SAME ⋊-SHAPE (orbit-rep, group-element) but its factors are coemit-local
--     (3 axes × perms, not 6 orbit-keys × 4 V₄) — an honest-partial: the shape matches, the carriers differ.
coemit-s4iso-shape : Set                       -- coemit's local ⋊-shape; the canonical form is S4Iso's TotalSpace
coemit-s4iso-shape = Σ GradingAxis (λ _ → V4.V4Full)   -- (Stab(D)-rep-ish , V₄-element) — the CANONICAL factor order
