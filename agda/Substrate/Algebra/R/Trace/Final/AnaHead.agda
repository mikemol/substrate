------------------------------------------------------------------------
-- Substrate.Algebra.R.Trace.Final.AnaHead
--
-- Defines: ana-head
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.Algebra.R.Trace.Final; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K --guardedness #-}

module Substrate.Algebra.R.Trace.Final.AnaHead where

open import Substrate.Foundation.Nat.Nat
open import Substrate.Foundation.Product
open import Substrate.Algebra.R.Trace
open import Substrate.Algebra.R.Trace.Unfold
open import Substrate.Foundation.Eq
open import Substrate.Algebra.R.Trace.Final.Coalg
open import Substrate.Algebra.R.Trace.Final.Ana



ana-head : {S : Set} (c : Coalg S) (s : S) → head (ana c s) ≡ proj₁ (c s)
ana-head c s = refl
