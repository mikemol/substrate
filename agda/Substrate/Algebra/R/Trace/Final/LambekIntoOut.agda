------------------------------------------------------------------------
-- Substrate.Algebra.R.Trace.Final.LambekIntoOut
--
-- Defines: lambek-into-out
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.Algebra.R.Trace.Final; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K --guardedness #-}

module Substrate.Algebra.R.Trace.Final.LambekIntoOut where

open import Substrate.Foundation.Nat.Nat
open import Substrate.Foundation.Product
open import Substrate.Algebra.R.Trace
open import Substrate.Algebra.R.Trace.Bisim.Cons
open import Substrate.Algebra.R.Trace.Bisim.Op
open import Substrate.Algebra.R.Trace.Bisim.Refl
open import Substrate.Foundation.Eq
open import Substrate.Algebra.R.Trace.Final.Out
open import Substrate.Algebra.R.Trace.Final.Into



lambek-into-out : (x : RealTrace) → into (out x) ~ x
head~ (lambek-into-out x) = refl
tail~ (lambek-into-out x) = ~-refl (tail x)
