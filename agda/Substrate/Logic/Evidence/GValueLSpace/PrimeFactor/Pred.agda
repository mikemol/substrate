------------------------------------------------------------------------
-- Substrate.Logic.Evidence.GValueLSpace.PrimeFactor.Pred
--
-- Defines: pred
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.Logic.Evidence.GValueLSpace.PrimeFactor; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Logic.Evidence.GValueLSpace.PrimeFactor.Pred where

open import Substrate.Foundation.Nat.Nat
open import Substrate.Algebra.Q.Rat
open import Substrate.Algebra.Z.Int
open import Substrate.Foundation.Eq
open import Substrate.Foundation.Eq.Cong
open import Substrate.Foundation.Eq.Cong2



pred : ℕ → ℕ
pred zero    = zero
pred (suc n) = n
