------------------------------------------------------------------------
-- Substrate.Algebra.R.Trace.Bisim.Refl
--
-- Defines: ~-refl
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.Algebra.R.Trace.Bisim; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K --guardedness #-}

module Substrate.Algebra.R.Trace.Bisim.Refl where

open import Substrate.Algebra.R.Trace
open import Substrate.Foundation.Eq
open import Substrate.Foundation.Eq.Sym
open import Substrate.Algebra.R.Trace.Bisim.Op



~-refl : (x : RealTrace) → x ~ x
head~ (~-refl x) = refl
tail~ (~-refl x) = ~-refl (tail x)
