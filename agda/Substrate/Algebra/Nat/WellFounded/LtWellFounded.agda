------------------------------------------------------------------------
-- Substrate.Algebra.Nat.WellFounded.LtWellFounded
--
-- Defines: <-wellFounded
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.Algebra.Nat.WellFounded; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.Nat.WellFounded.LtWellFounded where

open import Substrate.Foundation.Nat.Le
open import Substrate.Foundation.Nat.Lt
open import Substrate.Foundation.Nat.Nat
open import Substrate.Foundation.WellFounded
open import Substrate.Algebra.Nat.WellFounded.Private
open import Substrate.Algebra.Nat.WellFounded.AccSuc



<-wellFounded : WellFounded _<_
<-wellFounded zero    = acc (λ _ ())
<-wellFounded (suc n) = acc-suc (<-wellFounded n)
