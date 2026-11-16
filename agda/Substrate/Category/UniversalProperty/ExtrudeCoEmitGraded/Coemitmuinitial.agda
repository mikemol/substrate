------------------------------------------------------------------------
-- Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded.Coemitmuinitial
--
-- Defines: coemit-mu-initial
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K --guardedness #-}

module Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded.Coemitmuinitial where

open import Substrate.Algebra.R.Trace
open import Substrate.Algebra.R.Trace.Final.Into
open import Substrate.Algebra.R.Trace.Bisim.Op
open import Substrate.Category.Allegory.Refinement.Preamble
open import Substrate.Algebra.R.Trace.Bisim.Refl
  renaming (~-refl to ~-refl')
open import Substrate.Algebra.R.Trace.Final.Into
open import Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded.Zerotrace
open import Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded.Coemitmuunique
open import Substrate.Foundation.Product
open import Substrate.Foundation.Eq
open import Substrate.Groups.SemidirectProduct.Stab   -- Stab X σ = applyₛ σ X ≡ X (σ FIXES X)


-- (2) coemit-mu-initial: zero-trace as the INITIAL ALGEBRA fixed point. into (0 , zero-trace) = cons 0 zero-trace,
--     whose head is 0 and tail is zero-trace = zero-trace itself. So z IS the fixed point of the (0,-) algebra
--     (into ∘ (0,-)), the initial/least algebra — the dual of coemit-mu-unique (z the least fixed point).
coemit-mu-initial : into (0 , zero-trace) ~ zero-trace
head~ coemit-mu-initial = refl
tail~ coemit-mu-initial = ~-refl' zero-trace
