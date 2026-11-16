------------------------------------------------------------------------
-- Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded.Coemitout
--
-- Defines: coemit-out
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K --guardedness #-}

module Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded.Coemitout where

open import Substrate.Foundation.Nat.Nat
open import Substrate.Algebra.R.Trace
open import Substrate.Foundation.Product
open import Substrate.Category.Allegory.Refinement.Preamble
open import Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded.Tracemul
open import Substrate.Foundation.Eq
open import Substrate.Groups.SemidirectProduct.Stab   -- Stab X σ = applyₛ σ X ≡ X (σ FIXES X)


------------------------------------------------------------------------
-- coemit-mu-coalgebra-laws + coemit-mu-unique + coemit-colim-bridge: the μ-object's coalgebra structure, its
-- least-fixed-point universality, and the bridge to the finite-prefix presentation (337's continuations).
-- The F-coalgebra is Coalg S = S → ℕ × S (Trace.Final); out x = (head x , tail x). On a trace-mul product the
-- coalgebra map is out (trace-mul r s) = (0 , trace-mul (tail r)(tail s)) — EXACTLY diff-head + thread.
------------------------------------------------------------------------

-- (1) coemit-mu-coalgebra-laws: the carrier's coalgebra structure map — out on a trace-mul product IS (diff-head,
--     thread): the head-observation (0, the differential) paired with the threaded tail (the composition). A genuine
--     F-coalgebra step (Coalg RealTrace = RealTrace → ℕ × RealTrace) on the composition-carrier.
coemit-out : RealTrace → ℕ × RealTrace
coemit-out x = RealTrace.head x , RealTrace.tail x
