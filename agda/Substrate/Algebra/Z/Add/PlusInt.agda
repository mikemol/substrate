------------------------------------------------------------------------
-- Substrate.Algebra.Z.Add.PlusInt
--
-- Defines: _+ℤ_
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.Algebra.Z.Add; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.Z.Add.PlusInt where

open import Substrate.Foundation.Nat.Nat
open import Substrate.Foundation.Nat.Plus
open import Substrate.Algebra.Z.Int
open import Substrate.Algebra.Z.Add.Op

infixl 6 _+ℤ_


-- integer addition.
_+ℤ_ : ℤ → ℤ → ℤ
(+ m)    +ℤ (+ n)    = + (m ℕ+ n)
(+ m)    +ℤ (-suc n) = m ⊖ suc n
(-suc m) +ℤ (+ n)    = n ⊖ suc m
(-suc m) +ℤ (-suc n) = -suc suc (m ℕ+ n)
