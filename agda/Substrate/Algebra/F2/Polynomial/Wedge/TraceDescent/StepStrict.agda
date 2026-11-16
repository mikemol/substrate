------------------------------------------------------------------------
-- Substrate.Algebra.F2.Polynomial.Wedge.TraceDescent.StepStrict
--
-- Defines: step-strict
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.Algebra.F2.Polynomial.Wedge.TraceDescent; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.F2.Polynomial.Wedge.TraceDescent.StepStrict where

open import Substrate.Foundation.Nat.Le
open import Substrate.Foundation.Nat.Lt
open import Substrate.Foundation.Nat.Nat
open import Substrate.Foundation.Product
open import Substrate.Foundation.Vec
open import Substrate.Algebra.F2.F2
open import Substrate.Algebra.F2.Polynomial.Wedge.EEATrace
open import Substrate.Algebra.F2.Polynomial.Wedge.TraceDescent.Qdim
open import Substrate.Algebra.F2.Polynomial.Wedge.TraceDescent.LeRefl



-- per-step STRICT descent of the dimension measure (the Φ-chain descent,
-- concretely): the remainder's dimension < the divisor's dimension.
step-strict : (d : ℕ) (f-lo : Vec F₂ (suc d)) (a : QPoly)
            → qdim (div-rem d f-lo a) < qdim (divisor-q d f-lo)
step-strict d f-lo a = ≤-refl (suc (suc d))
