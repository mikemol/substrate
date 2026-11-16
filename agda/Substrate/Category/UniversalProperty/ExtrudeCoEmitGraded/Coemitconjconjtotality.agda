------------------------------------------------------------------------
-- Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded.Coemitconjconjtotality
--
-- Defines: coemit-conj-conj-totality
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K --guardedness #-}

module Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded.Coemitconjconjtotality where

open import Substrate.Foundation.Nat.Nat
open import Substrate.Algebra.R.Trace
open import Substrate.Category.Allegory.Refinement.Preamble
open import Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded.Coemiteqistotalitybwd
open import Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded.Bar
open import Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded.Coemitconjconj
open import Substrate.Foundation.Eq
open import Substrate.Groups.SemidirectProduct.Stab   -- Stab X σ = applyₛ σ X ≡ X (σ FIXES X)


-- the SAME fact as the TOTALITY over all finite perspectives (the orbit's actions) — 351's construction, exhibited.
coemit-conj-conj-totality : (r : RealTrace) (n : ℕ) → take n (bar (bar r)) ≡ take n r
coemit-conj-conj-totality r n = coemit-eq-is-totality-bwd r (bar (bar r)) (coemit-conj-conj r) n
