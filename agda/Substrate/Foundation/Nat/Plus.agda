------------------------------------------------------------------------
-- Substrate.Foundation.Nat.Plus
--
-- Defines: _ℕ+_
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.Foundation.Nat; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Foundation.Nat.Plus where

open import Substrate.Foundation.Nat.Nat

infixl 6 _ℕ+_


_ℕ+_ : ℕ → ℕ → ℕ
zero  ℕ+ n = n
suc m ℕ+ n = suc (m ℕ+ n)
