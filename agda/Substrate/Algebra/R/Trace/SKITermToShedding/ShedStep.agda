------------------------------------------------------------------------
-- Substrate.Algebra.R.Trace.SKITermToShedding.ShedStep
--
-- Defines: shed-step
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.Algebra.R.Trace.SKITermToShedding; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.R.Trace.SKITermToShedding.ShedStep where

open import Substrate.Foundation.Nat.Nat
open import Substrate.Algebra.Wedge.Graded
open import Substrate.Foundation.Eq
open import Substrate.Foundation.Eq.Cong
open import Substrate.Algebra.R.Trace.SKIShedDuality.Tm
open import Substrate.Algebra.R.Trace.SKITermToShedding.Cost
open import Substrate.Algebra.R.Trace.SKITermToShedding.SkiGraded



------------------------------------------------------------------------
-- 3. A SINGLE SHED as a GradedWedge: the term a (grade suc n) decomposes against its
-- function f (grade n) by the peeled argument, witnessed by the invertible rebuild.
-- CARRIES the cost in the grade AND the structure in the remainder — two indexes.
------------------------------------------------------------------------
shed-step : (n : ℕ) (f a : Tm) → GradedWedge ski-graded n (f ∙ a) f
shed-step n f a = record { rem = a ; wedge-eq = refl }   -- f∙a ≡ recon n f a = f∙a (refl)
