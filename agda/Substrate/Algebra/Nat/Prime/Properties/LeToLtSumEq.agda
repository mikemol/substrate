------------------------------------------------------------------------
-- Substrate.Algebra.Nat.Prime.Properties.LeToLtSumEq
--
-- Defines: ≤→<⊎≡
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.Algebra.Nat.Prime.Properties; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.Nat.Prime.Properties.LeToLtSumEq where

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



≤→<⊎≡ : (d b : ℕ) → d ≤ b → (d < b) ⊎ (d ≡ b)
≤→<⊎≡ zero    zero    _         = inj₂ refl
≤→<⊎≡ zero    (suc b) _         = inj₁ (s≤s z≤n)
≤→<⊎≡ (suc d) zero    ()
≤→<⊎≡ (suc d) (suc b) (s≤s d≤b) with ≤→<⊎≡ d b d≤b
... | inj₁ d<b = inj₁ (s≤s d<b)
... | inj₂ d≡b = inj₂ (cong suc d≡b)
