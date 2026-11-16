------------------------------------------------------------------------
-- Substrate.Algebra.R.Trace.Final.Coalg
--
-- Defines: Coalg
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.Algebra.R.Trace.Final; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K --guardedness #-}

module Substrate.Algebra.R.Trace.Final.Coalg where

open import Substrate.Foundation.Nat.Nat
open import Substrate.Foundation.Product



------------------------------------------------------------------------
-- The stream functor S(X) = ℕ × X. A coalgebra is a state machine S → ℕ × S.
------------------------------------------------------------------------

Coalg : Set → Set
Coalg S = S → ℕ × S
