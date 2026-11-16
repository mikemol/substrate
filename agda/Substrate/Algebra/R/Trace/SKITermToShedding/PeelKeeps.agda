------------------------------------------------------------------------
-- Substrate.Algebra.R.Trace.SKITermToShedding.PeelKeeps
--
-- Defines: peel-keeps
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.Algebra.R.Trace.SKITermToShedding; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.R.Trace.SKITermToShedding.PeelKeeps where

open import Substrate.Foundation.Nat.Nat
open import Substrate.Algebra.Wedge.Graded
open import Substrate.Foundation.Eq
open import Substrate.Foundation.Eq.Cong
open import Substrate.Algebra.R.Trace.SKIShedDuality.Tm
open import Substrate.Algebra.R.Trace.SKITermToShedding.ShedPeel



-- the peel read keeps the REAL subterm a (not zero) — the structure index carried.
peel-keeps : (n : ℕ) (f a : Tm) → shed-peel n f a ≡ a
peel-keeps n f a = refl
