------------------------------------------------------------------------
-- Substrate.Algebra.R.Trace.Bisim.Trans
--
-- Defines: ~-trans
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.Algebra.R.Trace.Bisim; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K --guardedness #-}

module Substrate.Algebra.R.Trace.Bisim.Trans where

open import Substrate.Algebra.R.Trace
open import Substrate.Foundation.Eq
open import Substrate.Foundation.Eq.Sym
open import Substrate.Foundation.Eq.TransSym
open import Substrate.Algebra.R.Trace.Bisim.Op



~-trans : {x y z : RealTrace} → x ~ y → y ~ z → x ~ z
head~ (~-trans p q) = trans-sym (head~ p) (sym (head~ q))
tail~ (~-trans p q) = ~-trans (tail~ p) (tail~ q)
