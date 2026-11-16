------------------------------------------------------------------------
-- Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded.Coemitmuanaunique
--
-- Defines: coemit-mu-ana-unique
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K --guardedness #-}

module Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded.Coemitmuanaunique where

open import Substrate.Foundation.Nat.Nat
open import Substrate.Algebra.R.Trace
open import Substrate.Algebra.R.Trace.Final.Ana
open import Substrate.Algebra.R.Trace.Final.AnaUnique
open import Substrate.Algebra.R.Trace.Bisim.Op
open import Substrate.Category.Allegory.Refinement.Preamble
open import Substrate.Algebra.R.Trace.Final.Ana
open import Substrate.Algebra.R.Trace.Final.AnaUnique
open import Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded.Coemitout
open import Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded.Coemitmuana
open import Substrate.Foundation.Eq
open import Substrate.Groups.SemidirectProduct.Stab   -- Stab X σ = applyₛ σ X ≡ X (σ FIXES X)


-- ana coemit-out is the unique such morphism: any h respecting coemit-out's head/tail is ~ it (finality/uniqueness).
coemit-mu-ana-unique : (h : RealTrace → RealTrace)
                     → (∀ x → RealTrace.head (h x) ≡ RealTrace.head x)
                     → (∀ x → RealTrace.tail (h x) ≡ h (RealTrace.tail x))
                     → (x : RealTrace) → h x ~ coemit-mu-ana x
coemit-mu-ana-unique h hh ht = ana-unique coemit-out h hh ht
