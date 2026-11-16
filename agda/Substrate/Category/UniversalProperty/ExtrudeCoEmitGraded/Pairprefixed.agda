------------------------------------------------------------------------
-- Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded.Pairprefixed
--
-- Defines: pair-pre-fixed
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K --guardedness #-}

module Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded.Pairprefixed where

open import Substrate.Foundation.Nat.Nat
open import Substrate.Algebra.R.Trace
open import Substrate.Category.Allegory.Refinement.Preamble
open import Substrate.Category.Allegory.Refinement.Refinement
open import Substrate.Category.UniversalProperty.ExtrudeCoEmitViaTrace.CoemitTrace
open import Substrate.Foundation.Unit
open import Substrate.Category.Allegory.Refinement.Refinement
open import Substrate.Category.Allegory.Refinement.Preamble
open import Substrate.Category.Allegory.Refinement.Refinement
open import Substrate.Algebra.R.Trace.Bisim.Trans
open import Substrate.Algebra.R.Trace.Bisim.Refl
open import Substrate.Foundation.Fin.Fin
open import Substrate.Foundation.Fin.Fin
open import Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded.Obs
open import Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded.Anon
open import Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded.Pairexact
open import Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded.Coemitrefinementpair
open import Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded.Ppair
open import Substrate.Foundation.Eq
open import Substrate.Groups.SemidirectProduct.Stab   -- Stab X σ = applyₛ σ X ≡ X (σ FIXES X)
open import Substrate.Foundation.Eq.Cong
open import Substrate.Foundation.Eq.Sym
open import Substrate.Foundation.Eq.Trans


------------------------------------------------------------------------
-- pair-refinement-chain: the DESCENDING Φ-chain for coemit-refinement-pair (genuinely SHRINKING, unlike Φ-obs 319).
-- The pre-fixed-point is trivial (target ⊤); Refinement.chain gives Riterate (suc n) ⊑ᶠ Riterate n — each grade
-- adds a head-agreement constraint, so the chain properly descends (fewer inhabitants). The gfp = the ~-class.
------------------------------------------------------------------------

pair-pre-fixed : Φ-pair-exact P⁰-pair R⊑ᶠ P⁰-pair
pair-pre-fixed rt _ = tt
