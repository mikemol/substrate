------------------------------------------------------------------------
-- Substrate.Algebra.Nat.Mod.ModSucBound
--
-- Defines: mod-suc-bound
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.Algebra.Nat.Mod; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.Nat.Mod.ModSucBound where

open import Substrate.Foundation.Nat.Le
open import Substrate.Foundation.Nat.Lt
open import Substrate.Foundation.Nat.Lt2
open import Substrate.Foundation.Nat.Nat
open import Substrate.Foundation.Negation.Dec
open import Substrate.Foundation.Negation.Preamble
open import Substrate.Foundation.Nat.Nat.ModSuc



------------------------------------------------------------------------
-- 2. The remainder-bound.
--
-- `a mod-suc b < suc b` always: the result lives in {0, 1, …, b}.
-- Proof by induction on `a`, dispatching on the same with-clause
-- that defines `_mod-suc_`.
------------------------------------------------------------------------

mod-suc-bound : (a b : ℕ) → (a mod-suc b) < suc b
mod-suc-bound zero    b = s≤s z≤n
mod-suc-bound (suc a) b with suc (a mod-suc b) <? suc b
... | yes sr<sb = sr<sb
... | no  _     = s≤s z≤n
