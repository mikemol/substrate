------------------------------------------------------------------------
-- Substrate.Algebra.F2.Polynomial.Wedge.DegreeBound.MLemPlusn
--
-- Defines: m≤m+n
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.Algebra.F2.Polynomial.Wedge.DegreeBound; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.F2.Polynomial.Wedge.DegreeBound.MLemPlusn where

open import Substrate.Foundation.Nat.Le
open import Substrate.Foundation.Nat.Lt
open import Substrate.Foundation.Nat.Nat
open import Substrate.Foundation.Nat.Plus
open import Substrate.Algebra.F2.F2
open import Substrate.Algebra.F2.Polynomial.Utilities.LeadingPosition
open import Substrate.Foundation.Eq
open import Substrate.Foundation.Eq.Sym
open import Substrate.Foundation.Eq.Cong
open import Substrate.Foundation.Eq.Subst


m≤m+n : (m n : ℕ) → m ≤ m ℕ+ n
m≤m+n zero    n = z≤n
m≤m+n (suc m) n = s≤s (m≤m+n m n)
-- leading-position-acc [] reduces to best (forced here, where refl typechecks).
