------------------------------------------------------------------------
-- Substrate.Algebra.R.Trace.Final.LambekOutInto
--
-- Defines: lambek-out-into
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.Algebra.R.Trace.Final; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K --guardedness #-}

module Substrate.Algebra.R.Trace.Final.LambekOutInto where

open import Substrate.Foundation.Nat.Nat
open import Substrate.Foundation.Product
open import Substrate.Algebra.R.Trace
open import Substrate.Algebra.R.Trace.Bisim.Cons
open import Substrate.Foundation.Eq
open import Substrate.Algebra.R.Trace.Final.Out
open import Substrate.Algebra.R.Trace.Final.Into



lambek-out-into : (ns : ℕ × RealTrace) → out (into ns) ≡ ns
lambek-out-into (n , x) = refl
