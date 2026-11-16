------------------------------------------------------------------------
-- Substrate.Algebra.R.Trace.Bisim.Op
--
-- Defines: _~_, head~, tail~
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.Algebra.R.Trace.Bisim; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K --guardedness #-}

module Substrate.Algebra.R.Trace.Bisim.Op where

open import Substrate.Algebra.R.Trace
open import Substrate.Foundation.Eq
open import Substrate.Foundation.Eq.Sym



------------------------------------------------------------------------
-- Bisimilarity: observational equality of suspended generators.
------------------------------------------------------------------------

record _~_ (x y : RealTrace) : Set where      -- ⟦shape:f7f76433 field head~,tail~⟧
  coinductive
  field head~ : head x ≡ head y
        tail~ : tail x ~ tail y
open _~_ public
