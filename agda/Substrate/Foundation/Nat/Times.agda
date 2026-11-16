------------------------------------------------------------------------
-- Substrate.Foundation.Nat.Times
--
-- Defines: _*_
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.Foundation.Nat; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Foundation.Nat.Times where

open import Substrate.Foundation.Nat.Nat
open import Substrate.Foundation.Nat.Plus

infixl 7 _*_


_*_ : ℕ → ℕ → ℕ
zero  * n = zero
suc m * n = n ℕ+ (m * n)
