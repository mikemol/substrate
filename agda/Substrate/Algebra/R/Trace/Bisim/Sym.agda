------------------------------------------------------------------------
-- Substrate.Algebra.R.Trace.Bisim.Sym
--
-- Defines: ~-sym
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.Algebra.R.Trace.Bisim; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K --guardedness #-}

module Substrate.Algebra.R.Trace.Bisim.Sym where

open import Substrate.Algebra.R.Trace
open import Substrate.Foundation.Eq
open import Substrate.Foundation.Eq.Sym
open import Substrate.Algebra.R.Trace.Bisim.Op



-- symmetry + transitivity: completing the equivalence of _~_ AT ITS CANONICAL HOME, so every structure that
-- factors through the terminal RealTrace inherits the WHOLE equivalence (not just reflexivity).
~-sym : {x y : RealTrace} → x ~ y → y ~ x
head~ (~-sym p) = sym (head~ p)
tail~ (~-sym p) = ~-sym (tail~ p)
