------------------------------------------------------------------------
-- Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded.Coemitdaggerisgroupoidinverse
--
-- Defines: coemit-dagger-is-groupoid-inverse
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K --guardedness #-}

module Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded.Coemitdaggerisgroupoidinverse where

open import Substrate.Algebra.R.Trace
open import Substrate.Algebra.R.Trace.Bisim.Op
open import Substrate.Algebra.R.Trace.Bisim.Sym
open import Substrate.Category.Allegory.Refinement.Preamble
open import Substrate.Algebra.R.Trace.Bisim.Sym
open import Substrate.Foundation.Eq
open import Substrate.Groups.SemidirectProduct.Stab   -- Stab X σ = applyₛ σ X ≡ X (σ FIXES X)


-- THE SHARED C₂: the dagger † is a self-inverse (an involution) present in BOTH V₄s. Its coemit shadow is the
-- ~-symmetry (the groupoid inverse ~-sym, StarV4's "THE ARROW: the groupoid's inverse iso-sym IS the dagger").
coemit-dagger-is-groupoid-inverse : {r s : RealTrace} → r ~ s → s ~ r
coemit-dagger-is-groupoid-inverse = ~-sym      -- the ARROW's dagger † (self-inverse) = the ~-groupoid's inverse
