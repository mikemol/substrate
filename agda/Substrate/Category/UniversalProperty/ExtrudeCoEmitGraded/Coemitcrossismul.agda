------------------------------------------------------------------------
-- Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded.Coemitcrossismul
--
-- Defines: coemit-cross-is-mul
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K --guardedness #-}

module Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded.Coemitcrossismul where

open import Substrate.Algebra.R.Trace
open import Substrate.Algebra.R.Trace.Bisim.Op
open import Substrate.Category.Allegory.Refinement.Preamble
open import Substrate.Algebra.Wedge.CrossMul
open import Substrate.Algebra.Wedge.Bridge
open import Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded.Zerotrace
open import Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded.Tracemul
open import Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded.Tracemulcollapses
open import Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded.Coemitcrossmix
open import Substrate.Foundation.Eq
open import Substrate.Groups.SemidirectProduct.Stab   -- Stab X σ = applyₛ σ X ≡ X (σ FIXES X)


-- the cross term = trace-mul of the two traces (translated by id-bridge = themselves); its nilpotency = Coherent.
-- trace-mul collapses to z at degree 1 (pow 1 = trace-mul r t ~ z, ε²=z shape) — coherence everywhere (μ frame).
coemit-cross-is-mul : (r t : RealTrace) → cross coemit-crossmix r t ~ zero-trace
coemit-cross-is-mul r t = trace-mul-collapses r t
