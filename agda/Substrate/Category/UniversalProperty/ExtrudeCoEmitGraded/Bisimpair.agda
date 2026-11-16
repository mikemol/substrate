------------------------------------------------------------------------
-- Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded.Bisimpair
--
-- Defines: bisim→νΦ-pair
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K --guardedness #-}

module Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded.Bisimpair where

open import Substrate.Foundation.Nat.Nat
open import Substrate.Algebra.R.Trace
open import Substrate.Algebra.R.Trace.Bisim.Op
open import Substrate.Category.Allegory.Refinement.Preamble
open import Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded.Pairagreeiter
open import Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded.Bisimprefix
open import Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded.Pair
open import Substrate.Foundation.Product
open import Substrate.Foundation.Eq
open import Substrate.Groups.SemidirectProduct.Stab   -- Stab X σ = applyₛ σ X ≡ X (σ FIXES X)
open import Substrate.Foundation.Eq.Cong


bisim→νΦ-pair : (r t : RealTrace) → t ~ r → νΦ-pair (r , t)
bisim→νΦ-pair r t p n = pair-agree→iter n r t (bisim→prefix n r t p)
