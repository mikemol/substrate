------------------------------------------------------------------------
-- Substrate.Algebra.F2.Polynomial.Wedge.DegreeBound.LpAccBound
--
-- Defines: lp-acc-bound
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.Algebra.F2.Polynomial.Wedge.DegreeBound; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.F2.Polynomial.Wedge.DegreeBound.LpAccBound where

open import Substrate.Foundation.Nat.Le
open import Substrate.Foundation.Nat.Lt
open import Substrate.Foundation.Nat.Nat
open import Substrate.Foundation.Nat.Plus
open import Substrate.Foundation.Maybe
open import Substrate.Foundation.Vec
open import Substrate.Algebra.F2.F2
open import Substrate.Algebra.F2.Polynomial
open import Substrate.Algebra.F2.Polynomial.Utilities.LeadingPosition
open import Substrate.Algebra.F2.Polynomial.Wedge.DegreeLt
open import Substrate.Foundation.Eq
open import Substrate.Foundation.Eq.Sym
open import Substrate.Foundation.Eq.Cong
open import Substrate.Foundation.Eq.Subst
open import Substrate.Algebra.F2.Polynomial.Wedge.DegreeBound.PlusSuc
open import Substrate.Algebra.F2.Polynomial.Wedge.DegreeBound.LeTrans
open import Substrate.Algebra.F2.Polynomial.Wedge.DegreeBound.MLemPlusn
open import Substrate.Algebra.F2.Polynomial.Wedge.DegreeBound.LpEmpty



-- the leading position counted from `pos` over a length-n tail is < pos+n ≤ N.
lp-acc-bound : ∀ {n} (v : Polynomial n) (pos : ℕ) (best : Maybe ℕ) (N : ℕ)
             → pos ℕ+ n ≤ N → degree-lt best (just N)
             → degree-lt (leading-position-acc v pos best) (just N)
lp-acc-bound {zero}  [] pos best N h1 h2 =
  subst (λ z → degree-lt z (just N)) (sym (lp-empty pos best)) h2
lp-acc-bound (𝟘 ∷ p) pos best N h1 h2 =
  lp-acc-bound p (suc pos) best N (subst (_≤ N) (+-suc pos _) h1) h2
lp-acc-bound (𝟙 ∷ p) pos best N h1 h2 =
  lp-acc-bound p (suc pos) (just pos) N (subst (_≤ N) (+-suc pos _) h1)
               (≤-trans (s≤s (m≤m+n pos _)) (subst (_≤ N) (+-suc pos _) h1))
