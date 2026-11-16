------------------------------------------------------------------------
-- Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded.Perspectiveisfinitecycaper
--
-- Defines: perspective-is-finite-cyc-aper
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K --guardedness #-}

module Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded.Perspectiveisfinitecycaper where

open import Substrate.Foundation.Nat.Nat
open import Substrate.Foundation.Vec
open import Substrate.Algebra.R.Trace
open import Substrate.Category.Allegory.Refinement.Preamble
open import Substrate.Foundation.Fin.Fin
open import Substrate.Foundation.Fin.Fin
open import Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded.Len
open import Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded.Perspectivefinite
open import Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded.GradingAxis
open import Substrate.Foundation.Eq
open import Substrate.Groups.SemidirectProduct.Stab   -- Stab X σ = applyₛ σ X ≡ X (σ FIXES X)
open import Substrate.Foundation.Eq.Cong


perspective-is-finite-cyc-aper : (r : RealTrace) (n : ℕ) → len (perspective-finite cyc-aper-axis r n) ≡ n
perspective-is-finite-cyc-aper r zero    = refl
perspective-is-finite-cyc-aper r (suc n) = cong suc (perspective-is-finite-cyc-aper (RealTrace.tail r) n)
