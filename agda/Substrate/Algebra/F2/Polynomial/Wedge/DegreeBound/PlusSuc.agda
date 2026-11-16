------------------------------------------------------------------------
-- Substrate.Algebra.F2.Polynomial.Wedge.DegreeBound.PlusSuc
--
-- Defines: +-suc
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.Algebra.F2.Polynomial.Wedge.DegreeBound; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.F2.Polynomial.Wedge.DegreeBound.PlusSuc where

open import Substrate.Foundation.Nat.Le
open import Substrate.Foundation.Nat.Lt
open import Substrate.Foundation.Nat.Nat
open import Substrate.Foundation.Nat.Plus
open import Substrate.Algebra.F2.F2
open import Substrate.Foundation.Eq
open import Substrate.Foundation.Eq.Sym
open import Substrate.Foundation.Eq.Cong
open import Substrate.Foundation.Eq.Subst



+-suc : (m n : ℕ) → m ℕ+ suc n ≡ suc (m ℕ+ n)
+-suc zero    n = refl
+-suc (suc m) n = cong suc (+-suc m n)
