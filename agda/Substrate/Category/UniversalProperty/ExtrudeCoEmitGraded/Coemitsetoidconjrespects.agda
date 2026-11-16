------------------------------------------------------------------------
-- Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded.Coemitsetoidconjrespects
--
-- Defines: coemit-setoid-conj-respects
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K --guardedness #-}

module Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded.Coemitsetoidconjrespects where

open import Substrate.Algebra.R.Trace
open import Substrate.Algebra.R.Trace.Bisim.Op
open import Substrate.Category.Allegory.Refinement.Preamble

open import Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded.Bar
open import Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded.Coemitconjconj
open import Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded.Barcong
open import Substrate.Foundation.Eq
open import Substrate.Groups.SemidirectProduct.Stab   -- Stab X σ = applyₛ σ X ≡ X (σ FIXES X)
open import Substrate.Foundation.Eq.Cong


-- the setoid-StarDivStr components: conj respects ≈ (bar-cong), and conj∘conj ≈ id (coemit-conj-conj).
coemit-setoid-conj-respects : {r s : RealTrace} → r ~ s → bar r ~ bar s
coemit-setoid-conj-respects = bar-cong
