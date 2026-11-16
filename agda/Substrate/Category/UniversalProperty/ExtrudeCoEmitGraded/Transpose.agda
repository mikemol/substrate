------------------------------------------------------------------------
-- Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded.Transpose
--
-- Defines: transpose
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K --guardedness #-}

module Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded.Transpose where

open import Substrate.Algebra.R.Trace
open import Substrate.Algebra.R.Trace.Bisim.Op
open import Substrate.Algebra.R.Trace.Bisim.Sym
open import Substrate.Category.Allegory.Refinement.Preamble
open import Substrate.Algebra.R.Trace.Bisim.Sym
open import Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded.Bar
open import Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded.Barcong
open import Substrate.Foundation.Eq
open import Substrate.Groups.SemidirectProduct.Stab   -- Stab X σ = applyₛ σ X ≡ X (σ FIXES X)
open import Substrate.Foundation.Eq.Cong


------------------------------------------------------------------------
-- (2) coemit-transpose-adjoint: StarV4's FOURTH V₄ element — "the fourth element † ∘ bar is the TRANSPOSE/ADJOINT".
--     † is the groupoid's inverse (IsoGroupoid.iso-sym; on coemit's ~-groupoid that is ~-sym, 349).
--     bar is the conjugation (352). Their composite acts on ~-proofs: p : r ~ s ↦ bar s ~ bar r.
------------------------------------------------------------------------
transpose : {r s : RealTrace} → r ~ s → bar s ~ bar r
transpose p = ~-sym (bar-cong p)          -- † ∘ bar — the transpose/adjoint (StarV4's fourth element)
