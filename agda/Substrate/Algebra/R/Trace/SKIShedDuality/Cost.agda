------------------------------------------------------------------------
-- Substrate.Algebra.R.Trace.SKIShedDuality.Cost
--
-- Defines: cost
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.Algebra.R.Trace.SKIShedDuality; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K --guardedness #-}

module Substrate.Algebra.R.Trace.SKIShedDuality.Cost where

open import Substrate.Foundation.Nat.Nat
open import Substrate.Foundation.Nat.Plus
open import Substrate.Algebra.R.Trace.Bisim.Op
open import Substrate.Algebra.R.Trace.Bisim.Refl
open import Substrate.Foundation.Eq
open import Substrate.Algebra.R.Trace.SKIShedDuality.Tm



-- the head-redex cost shed by contracting once (the Nf obstruction, ADD 130-142).
cost : Tm → ℕ
cost (I ∙ x)             = 1
cost ((K ∙ x) ∙ y)       = 1
cost (((S ∙ x) ∙ y) ∙ z) = 1
cost _                   = 0
