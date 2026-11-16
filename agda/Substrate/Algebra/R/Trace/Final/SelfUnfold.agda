------------------------------------------------------------------------
-- Substrate.Algebra.R.Trace.Final.SelfUnfold
--
-- Defines: self-unfold
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.Algebra.R.Trace.Final; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K --guardedness #-}

module Substrate.Algebra.R.Trace.Final.SelfUnfold where

open import Substrate.Foundation.Nat.Nat
open import Substrate.Foundation.Product
open import Substrate.Algebra.R.Trace
open import Substrate.Algebra.R.Trace.Unfold
open import Substrate.Algebra.R.Trace.Bisim.Op
open import Substrate.Foundation.Eq
open import Substrate.Algebra.R.Trace.Final.Out
open import Substrate.Algebra.R.Trace.Final.Ana
open import Substrate.Algebra.R.Trace.Final.AnaUnique



------------------------------------------------------------------------
-- The h = id corollary: every generator IS the unfold of its own observations.
-- So "is this generator the right number?" is not a theorem to discharge against
-- an external value — the generator is canonical up to `~`, and any presentation
-- with the same structure map is `~` to it (ana-unique). Presentation-uniqueness
-- is routine; there is no privileged "true value" to match.
------------------------------------------------------------------------

self-unfold : (x : RealTrace) → x ~ ana out x
head~ (self-unfold x) = refl
tail~ (self-unfold x) = self-unfold (tail x)
