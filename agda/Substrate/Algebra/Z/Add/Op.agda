------------------------------------------------------------------------
-- Substrate.Algebra.Z.Add.Op
--
-- Defines: _⊖_
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.Algebra.Z.Add; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.Z.Add.Op where

open import Substrate.Foundation.Nat.Nat
open import Substrate.Foundation.Nat.Plus
open import Substrate.Algebra.Z.Int

infixl 6 _⊖_


-- truncated difference of two naturals AS an integer: m ⊖ n = m − n.
_⊖_ : ℕ → ℕ → ℤ
m     ⊖ zero  = + m
zero  ⊖ suc n = -suc n
suc m ⊖ suc n = m ⊖ n
