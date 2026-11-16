------------------------------------------------------------------------
-- Substrate.Algebra.F2.Polynomial.Wedge.DegreeBound.LpBound
--
-- Defines: lp-bound
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.Algebra.F2.Polynomial.Wedge.DegreeBound; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.F2.Polynomial.Wedge.DegreeBound.LpBound where

open import Substrate.Foundation.Nat.Le
open import Substrate.Foundation.Nat.Lt
open import Substrate.Foundation.Nat.Nat
open import Substrate.Foundation.Nat.Plus
open import Substrate.Foundation.Maybe
open import Substrate.Foundation.Unit
open import Substrate.Foundation.Vec
open import Substrate.Algebra.F2.F2
open import Substrate.Algebra.F2.Polynomial
open import Substrate.Algebra.F2.Polynomial.Utilities.LeadingPosition
open import Substrate.Algebra.F2.Polynomial.Wedge.DegreeLt
open import Substrate.Foundation.Eq
open import Substrate.Foundation.Eq.Sym
open import Substrate.Foundation.Eq.Cong
open import Substrate.Foundation.Eq.Subst
open import Substrate.Algebra.F2.Polynomial.Wedge.DegreeBound.LeRefl
open import Substrate.Algebra.F2.Polynomial.Wedge.DegreeBound.LpAccBound



-- a Polynomial n has degree < n — the canonicality bound (applied to r-div a : Poly (suc d)).
lp-bound : ∀ {n} (v : Polynomial n) → degree-lt (leading-position v) (just n)
lp-bound {n} v = lp-acc-bound v 0 nothing n (≤-refl n) tt
