------------------------------------------------------------------------
-- Substrate.Foundation.Nat.Pow
--
-- Defines: _^_
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.Foundation.Nat; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Foundation.Nat.Pow where

open import Substrate.Foundation.Nat.Nat
open import Substrate.Foundation.Nat.Times

infixr 8 _^_


_^_ : ℕ → ℕ → ℕ
m ^ zero  = suc zero
m ^ suc n = m * (m ^ n)
