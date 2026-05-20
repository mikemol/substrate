------------------------------------------------------------------------
-- Substrate.Algebra.GL3F2.SingerOrder
--
-- HasOrder-singer : the Sylow-7 generator singer-Linear has order 7
-- as a linear endomap of Vector 3. The missing companion to S4's
-- GaugeGenerators (which delivered orders for Sylow-2 and Sylow-3 via
-- the mechanical HasOrder-from-perm combinator; singer is not a basis
-- permutation, so requires this dedicated proof).
--
-- Strategy. Vector 3 = Vec F₂ 3 has exactly 2³ = 8 inhabitants (each
-- component independently 𝟘 or 𝟙). For each inhabitant, the chain
-- iterate 7 (apply singer-Linear) reduces by Agda's evaluator —
-- apply singer-Linear v unfolds to a sum over basis images, which
-- reduces on concrete vector patterns.
--
-- This is finite enumeration justified by the small carrier size; for
-- larger carriers a more structural argument (e.g., bridging through
-- FanoPlane.singer⁷-id on Points) would be preferred per
-- [[expose-generator-not-orbit]]. Here, enumeration is appropriate
-- because Vector 3 IS the orbit: 1 zero + 7 nonzero (= Fano points)
-- = 8 cases.
--
-- Per [[multi-route-equivariance-recovery]]: with this slice, all
-- three Sylow generators carry HasOrder witnesses. S5 can now package
-- them as GL3F2 values and state the joint-generation theorem.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.GL3F2.SingerOrder where

open import Data.Vec using (_∷_; [])
open import Relation.Binary.PropositionalEquality using (_≡_; refl)

open import Substrate.Algebra.F2 using (F₂; 𝟘; 𝟙)
open import Substrate.Algebra.F2.Vector using (Vector)
open import Substrate.Algebra.F2.Linear using (apply)
open import Substrate.Algebra.F2.FanoPlane using (singer-Linear)
open import Substrate.Category.Coalgebra.FiniteOrder using (HasOrder)

------------------------------------------------------------------------
-- HasOrder-singer: iterate 7 (apply singer-Linear) v ≡ v for every
-- v : Vector 3. By pattern-matching on the 8 inhabitants of
-- Vec F₂ 3 = (F₂ × F₂ × F₂); each case reduces by evaluator after
-- Agda unfolds the 7 nested apply singer-Linear invocations.
------------------------------------------------------------------------

HasOrder-singer : HasOrder (apply singer-Linear) 7
HasOrder-singer (𝟘 ∷ 𝟘 ∷ 𝟘 ∷ []) = refl
HasOrder-singer (𝟙 ∷ 𝟘 ∷ 𝟘 ∷ []) = refl
HasOrder-singer (𝟘 ∷ 𝟙 ∷ 𝟘 ∷ []) = refl
HasOrder-singer (𝟘 ∷ 𝟘 ∷ 𝟙 ∷ []) = refl
HasOrder-singer (𝟙 ∷ 𝟙 ∷ 𝟘 ∷ []) = refl
HasOrder-singer (𝟙 ∷ 𝟘 ∷ 𝟙 ∷ []) = refl
HasOrder-singer (𝟘 ∷ 𝟙 ∷ 𝟙 ∷ []) = refl
HasOrder-singer (𝟙 ∷ 𝟙 ∷ 𝟙 ∷ []) = refl
