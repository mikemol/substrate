------------------------------------------------------------------------
-- Substrate.Foundation.Nat.Lt
--
-- Defines: _<_
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.Foundation.Nat; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Foundation.Nat.Lt where

open import Substrate.Foundation.Nat.Nat
open import Substrate.Foundation.Nat.Le

infix 4 _<_


_<_ : ℕ → ℕ → Set
m < n = suc m ≤ n
