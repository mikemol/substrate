------------------------------------------------------------------------
-- Substrate.Algebra.R.Trace.SKITermToShedding.CostCarriedI
--
-- Defines: cost-carried-I
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.Algebra.R.Trace.SKITermToShedding; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.R.Trace.SKITermToShedding.CostCarriedI where

open import Substrate.Foundation.Nat.Nat
open import Substrate.Foundation.Eq
open import Substrate.Foundation.Eq.Cong
open import Substrate.Algebra.R.Trace.SKIShedDuality.Tm
open import Substrate.Algebra.R.Trace.SKITermToShedding.Cost



-- the grade carries the REAL cost: shedding a head-redex term at grade (cost t)
-- records cost t, not zero. E.g. an I-redex sheds at grade 1, an S-triple at grade 1,
-- a non-redex at grade 0 — the actual head weight, per term.
cost-carried-I : (x : Tm)     → cost (I ∙ x) ≡ 1
cost-carried-I x = refl
