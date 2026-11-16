------------------------------------------------------------------------
-- Substrate.Algebra.R.Trace.Final.Ana
--
-- Defines: ana
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.Algebra.R.Trace.Final; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K --guardedness #-}

module Substrate.Algebra.R.Trace.Final.Ana where

open import Substrate.Foundation.Nat.Nat
open import Substrate.Foundation.Product
open import Substrate.Algebra.R.Trace
open import Substrate.Algebra.R.Trace.Unfold
open import Substrate.Algebra.R.Trace.Bisim.Cons
open import Substrate.Algebra.R.Trace.Final.Coalg
open import Substrate.Algebra.R.Trace.Final.Out
open import Substrate.Algebra.R.Trace.Final.Into



------------------------------------------------------------------------
-- ana = unfold: the unique coalgebra morphism from (S, c) into the terminal
-- coalgebra. The morphism square (out ∘ ana = (id × ana) ∘ c) holds by refl.
------------------------------------------------------------------------

ana : {S : Set} → Coalg S → S → RealTrace
ana = unfold
