------------------------------------------------------------------------
-- Substrate.Algebra.F2.Polynomial.Wedge.DegreeBound.LpEmpty
--
-- Defines: lp-empty
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.Algebra.F2.Polynomial.Wedge.DegreeBound; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.F2.Polynomial.Wedge.DegreeBound.LpEmpty where

open import Substrate.Foundation.Nat.Le
open import Substrate.Foundation.Nat.Lt
open import Substrate.Foundation.Nat.Nat
open import Substrate.Foundation.Nat.Plus
open import Substrate.Foundation.Maybe
open import Substrate.Algebra.F2.F2
open import Substrate.Algebra.F2.Polynomial.Utilities.LeadingPosition
open import Substrate.Foundation.Eq
open import Substrate.Foundation.Eq.Sym
open import Substrate.Foundation.Eq.Cong
open import Substrate.Foundation.Eq.Subst
open import Substrate.Foundation.Vec


lp-empty : (pos : ℕ) (best : Maybe ℕ) → leading-position-acc {0} [] pos best ≡ best
lp-empty pos best = refl
