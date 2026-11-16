------------------------------------------------------------------------
-- Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded.Coemitrefinementpair
--
-- Defines: coemit-refinement-pair
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K --guardedness #-}

module Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded.Coemitrefinementpair where

open import Substrate.Algebra.R.Trace
open import Substrate.Category.Allegory.Refinement.Preamble
open import Substrate.Category.Allegory.Refinement.Refinement
open import Substrate.Category.Allegory.Refinement.Refinement
open import Substrate.Category.Allegory.Refinement.Preamble
open import Substrate.Category.Allegory.Refinement.Refinement
open import Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded.RTPair
open import Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded.Pairexact
open import Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded.Pairexactmono
open import Substrate.Foundation.Eq
open import Substrate.Groups.SemidirectProduct.Stab   -- Stab X σ = applyₛ σ X ≡ X (σ FIXES X)


-- THE FORMAL REFINEMENT RECORD (contrast the degenerate coemit-refinement/Φ-obs; this one genuinely shrinks).
coemit-refinement-pair : Refinement RTPair Φ-pair-exact Φ-pair-exact-mono
coemit-refinement-pair = record {}
