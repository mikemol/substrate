------------------------------------------------------------------------
-- Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded.Coemitstardivstrconjconj
--
-- Defines: coemit-stardivstr-conj-conj
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K --guardedness #-}

module Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded.Coemitstardivstrconjconj where

open import Substrate.Algebra.R.Trace
open import Substrate.Algebra.R.Trace.Bisim.Op
open import Substrate.Category.Allegory.Refinement.Preamble
open import Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded.Coemitconjconj
open import Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded.Coemitstardivstrconj
open import Substrate.Foundation.Eq
open import Substrate.Groups.SemidirectProduct.Stab   -- Stab X σ = applyₛ σ X ≡ X (σ FIXES X)


coemit-stardivstr-conj-conj : (x : RealTrace) → coemit-stardivstr-conj (coemit-stardivstr-conj x) ~ x
coemit-stardivstr-conj-conj = coemit-conj-conj
