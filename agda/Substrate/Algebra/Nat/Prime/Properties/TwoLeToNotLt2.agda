------------------------------------------------------------------------
-- Substrate.Algebra.Nat.Prime.Properties.TwoLeToNotLt2
--
-- Defines: 2≤→¬<2
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.Algebra.Nat.Prime.Properties; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.Nat.Prime.Properties.TwoLeToNotLt2 where

open import Substrate.Foundation.Nat.Dec
open import Substrate.Foundation.Nat.Le
open import Substrate.Foundation.Nat.Lt
open import Substrate.Foundation.Nat.Nat
open import Substrate.Foundation.Nat.Plus
open import Substrate.Foundation.Nat.Times
open import Substrate.Foundation.Negation.Dec
open import Substrate.Foundation.Negation.Not
open import Substrate.Foundation.Empty.Bot
open import Substrate.Foundation.Empty.BotElim
open import Substrate.Foundation.Sum.Sum
open import Substrate.Foundation.Nat.Properties.Order
open import Substrate.Algebra.Quotient.ApproxcanonicalEq
open import Substrate.Algebra.Quotient.Canonical
open import Substrate.Algebra.Quotient.CanonicalEqApprox
open import Substrate.Algebra.Quotient.IdemCanonical
open import Substrate.Algebra.Quotient.KerQuotient
open import Substrate.Algebra.Quotient.KerRel
open import Substrate.Algebra.Quotient.Quotient
open import Substrate.Algebra.Quotient.SplitCanonical
open import Substrate.Foundation.Eq
open import Substrate.Foundation.Eq.Sym
open import Substrate.Foundation.Eq.Trans
open import Substrate.Foundation.Eq.Cong
open import Substrate.Foundation.Eq.Subst



------------------------------------------------------------------------
-- 3. The bounded least-divisor search → a primality decision.
------------------------------------------------------------------------

2≤→¬<2 : (d : ℕ) → 2 ≤ d → d < 2 → ⊥
2≤→¬<2 d 2≤d d<2 = <-irrefl 2 (≤-<-trans 2≤d d<2)
