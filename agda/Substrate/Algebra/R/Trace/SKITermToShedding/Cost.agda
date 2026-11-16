------------------------------------------------------------------------
-- Substrate.Algebra.R.Trace.SKITermToShedding.Cost
--
-- Defines: cost
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.Algebra.R.Trace.SKITermToShedding; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.R.Trace.SKITermToShedding.Cost where

open import Substrate.Foundation.Nat.Nat
open import Substrate.Foundation.Eq
open import Substrate.Foundation.Eq.Cong
open import Substrate.Algebra.R.Trace.SKIShedDuality.Tm



-- redex-cost: the head-redex weight shed by contracting once (I:1, K:1, S:1 arg-cost;
-- non-redex applications and atoms shed 0). The REAL value the flat trace discarded.
cost : Tm → ℕ
cost (I ∙ x)             = 1
cost ((K ∙ x) ∙ y)       = 1
cost (((S ∙ x) ∙ y) ∙ z) = 1
cost _                   = 0
