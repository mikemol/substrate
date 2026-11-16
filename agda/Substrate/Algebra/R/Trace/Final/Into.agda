------------------------------------------------------------------------
-- Substrate.Algebra.R.Trace.Final.Into
--
-- Defines: into
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.Algebra.R.Trace.Final; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K --guardedness #-}

module Substrate.Algebra.R.Trace.Final.Into where

open import Substrate.Foundation.Nat.Nat
open import Substrate.Foundation.Product
open import Substrate.Algebra.R.Trace
open import Substrate.Algebra.R.Trace.Bisim.Cons



into : ℕ × RealTrace → RealTrace
into (n , x) = cons n x
