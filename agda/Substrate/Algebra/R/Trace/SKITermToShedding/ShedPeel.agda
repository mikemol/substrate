------------------------------------------------------------------------
-- Substrate.Algebra.R.Trace.SKITermToShedding.ShedPeel
--
-- Defines: shed-peel
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.Algebra.R.Trace.SKITermToShedding; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.R.Trace.SKITermToShedding.ShedPeel where

open import Substrate.Foundation.Nat.Nat
open import Substrate.Algebra.Wedge.Graded
open import Substrate.Foundation.Eq
open import Substrate.Foundation.Eq.Cong
open import Substrate.Algebra.R.Trace.SKIShedDuality.Tm
open import Substrate.Algebra.R.Trace.SKITermToShedding.ShedStep



shed-peel : (n : ℕ) (f a : Tm) → Tm
shed-peel n f a = gcell (shed-step n f a)                 -- = a (the peeled digit)
