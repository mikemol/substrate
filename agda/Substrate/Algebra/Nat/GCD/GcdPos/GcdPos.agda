------------------------------------------------------------------------
-- Substrate.Algebra.Nat.GCD.GcdPos.GcdPos
--
-- Defines: gcd-pos
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.Algebra.Nat.GCD.GcdPos; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.Nat.GCD.GcdPos.GcdPos where

open import Substrate.Foundation.Nat.Le
open import Substrate.Foundation.Nat.Lt
open import Substrate.Foundation.Nat.Nat
open import Substrate.Foundation.Product
open import Substrate.Foundation.Empty.Bot
open import Substrate.Foundation.Empty.BotElim
open import Substrate.Foundation.Nat.Properties.Mul
open import Substrate.Algebra.Nat.Divides.Type
open import Substrate.Algebra.Nat.GCD.GcdN
open import Substrate.Algebra.Nat.GCD.GcdDividesRight
open import Substrate.Foundation.Eq
open import Substrate.Foundation.Eq.Sym
open import Substrate.Foundation.Eq.Trans
open import Substrate.Foundation.Eq.Subst
open import Substrate.Algebra.Nat.GCD.GcdPos.Zerosuc



gcd-pos : (n d : ℕ) → Σ ℕ (λ g′ → gcd-ℕ n (suc d) ≡ suc g′)
gcd-pos n d with gcd-ℕ n (suc d) | gcd-divides-right n (suc d)
... | zero  | z∣sd = ⊥-elim (zero∤suc z∣sd)
... | suc g | _    = g , refl
