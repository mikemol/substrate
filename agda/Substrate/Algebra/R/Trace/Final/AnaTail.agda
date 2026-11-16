------------------------------------------------------------------------
-- Substrate.Algebra.R.Trace.Final.AnaTail
--
-- Defines: ana-tail
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.Algebra.R.Trace.Final; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K --guardedness #-}

module Substrate.Algebra.R.Trace.Final.AnaTail where

open import Substrate.Foundation.Nat.Nat
open import Substrate.Foundation.Product
open import Substrate.Algebra.R.Trace
open import Substrate.Algebra.R.Trace.Unfold
open import Substrate.Foundation.Eq
open import Substrate.Algebra.R.Trace.Final.Coalg
open import Substrate.Algebra.R.Trace.Final.Ana



ana-tail : {S : Set} (c : Coalg S) (s : S) → tail (ana c s) ≡ ana c (proj₂ (c s))
ana-tail c s = refl
