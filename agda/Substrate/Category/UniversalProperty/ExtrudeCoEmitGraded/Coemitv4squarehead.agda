------------------------------------------------------------------------
-- Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded.Coemitv4squarehead
--
-- Defines: coemit-v4-square-head
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K --guardedness #-}

module Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded.Coemitv4squarehead where

open import Substrate.Foundation.Nat.Nat
open import Substrate.Algebra.R.Trace
open import Substrate.Algebra.R.Trace.Bisim.Op
open import Substrate.Algebra.R.Trace.Bisim.Sym
open import Substrate.Category.Allegory.Refinement.Preamble
open import Substrate.Algebra.R.Trace.Bisim.Sym
open import Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded.Transpose
open import Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded.Daggerbar
open import Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded.Natuip
open import Substrate.Foundation.Eq
open import Substrate.Groups.SemidirectProduct.Stab   -- Stab X σ = applyₛ σ X ≡ X (σ FIXES X)


-- the V₄ square at the HEAD (one step): the two routes †∘bar and bar∘† give the same head~ component.
coemit-v4-square-head : {r s : RealTrace} (p : r ~ s)
                      → head~ (transpose p) ≡ head~ (dagger-bar p)
coemit-v4-square-head p = nat-uip (head~ (transpose p)) (head~ (dagger-bar p))
