------------------------------------------------------------------------
-- Substrate.Algebra.R.Trace.SKIShedDuality.Shed
--
-- Defines: Shed, field, peeled, shed⟨_⟩
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.Algebra.R.Trace.SKIShedDuality; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K --guardedness #-}

module Substrate.Algebra.R.Trace.SKIShedDuality.Shed where

open import Substrate.Foundation.Nat.Nat
open import Substrate.Foundation.Nat.Plus
open import Substrate.Algebra.R.Trace.Bisim.Op
open import Substrate.Algebra.R.Trace.Bisim.Refl
open import Substrate.Foundation.Eq
open import Substrate.Algebra.R.Trace.SKIShedDuality.Tm



-- a shed at cost-grade n (carrying the peeled subterm) — the shared graded carrier.
record Shed (n : ℕ) : Set where
  constructor shed⟨_⟩
  field peeled : Tm
open Shed public
