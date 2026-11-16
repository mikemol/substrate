------------------------------------------------------------------------
-- Substrate.Algebra.R.Trace.SKIFaithfulRb.GenTotm
--
-- Defines: gen→tm
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.Algebra.R.Trace.SKIFaithfulRb; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.R.Trace.SKIFaithfulRb.GenTotm where

open import Substrate.Foundation.Nat.Nat
open import Substrate.Foundation.Eq
open import Substrate.Algebra.R.Trace.SKIFaithfulRb.Gen
open import Substrate.Algebra.R.Trace.SKIShedDuality.Tm



gen→tm : Gen-SKI → Tm
gen→tm gI = I
gen→tm gK = K
gen→tm gS = S
