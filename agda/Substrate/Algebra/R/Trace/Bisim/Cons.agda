------------------------------------------------------------------------
-- Substrate.Algebra.R.Trace.Bisim.Cons
--
-- Defines: cons
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.Algebra.R.Trace.Bisim; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K --guardedness #-}

module Substrate.Algebra.R.Trace.Bisim.Cons where

open import Substrate.Foundation.Nat.Nat
open import Substrate.Algebra.R.Trace
open import Substrate.Foundation.Eq.Sym



------------------------------------------------------------------------
-- A general CF cons (head k, tail t) — to name a real > 1.
------------------------------------------------------------------------

cons : ℕ → RealTrace → RealTrace
head (cons k x) = k
tail (cons k x) = x
