------------------------------------------------------------------------
-- Substrate.Algebra.R.Trace.NewmanSKI.Size
--
-- Defines: size
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.Algebra.R.Trace.NewmanSKI; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.R.Trace.NewmanSKI.Size where

open import Substrate.Foundation.Nat.Nat
open import Substrate.Foundation.Nat.Plus
open import Substrate.Algebra.R.Trace.SKIShedDuality.Tm



size : Tm → ℕ
size S = 1
size K = 1
size I = 1
size (f ∙ g) = suc (size f ℕ+ size g)
