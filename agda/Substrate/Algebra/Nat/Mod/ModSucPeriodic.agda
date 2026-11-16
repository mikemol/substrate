------------------------------------------------------------------------
-- Substrate.Algebra.Nat.Mod.ModSucPeriodic
--
-- Defines: mod-suc-periodic
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.Algebra.Nat.Mod; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.Nat.Mod.ModSucPeriodic where

open import Substrate.Foundation.Nat.Le
open import Substrate.Foundation.Nat.Lt
open import Substrate.Foundation.Nat.Lt2
open import Substrate.Foundation.Nat.Nat
open import Substrate.Foundation.Nat.Plus
open import Substrate.Foundation.Nat.Properties.Order.LeSucR
open import Substrate.Foundation.Nat.Properties.Order.LtIrrefl
open import Substrate.Foundation.Nat.Properties.Order.LtSucSelf
open import Substrate.Foundation.Empty.BotElim
open import Substrate.Foundation.Negation.Dec
open import Substrate.Foundation.Negation.Preamble
open import Substrate.Foundation.Nat.Nat.ModSuc
open import Substrate.Algebra.Nat.Mod.ModSucId
open import Substrate.Foundation.Eq
open import Substrate.Foundation.Eq.Cong
open import Substrate.Foundation.Eq.Subst
open import Substrate.Foundation.Eq.Sym



------------------------------------------------------------------------
-- 4. mod-suc-periodic — adding the modulus is identity in mod.
--
-- (a ℕ+ suc b) mod-suc b ≡ a mod-suc b. Proof by induction on a. The
-- base case uses mod-suc-id (b mod-suc b ≡ b) ℕ+ the with-clause
-- failing at suc b; the step case threads the IH through the with-
-- comparison.
------------------------------------------------------------------------

mod-suc-periodic : (a b : ℕ) → (a ℕ+ suc b) mod-suc b ≡ a mod-suc b
mod-suc-periodic zero b
  with suc (b mod-suc b) <? suc b
     | mod-suc-id b b (<-suc-self b)
... | yes lt  | bmodb≡b =
  ⊥-elim (<-irrefl b (subst (λ k → suc k ≤ b) bmodb≡b (s≤s-strip lt)))
  where
    s≤s-strip : ∀ {m n} → suc m < suc n → m < n
    s≤s-strip (s≤s p) = p
... | no  _   | _        = refl
mod-suc-periodic (suc a) b
  with suc ((a ℕ+ suc b) mod-suc b) <? suc b
     | suc (a mod-suc b)             <? suc b
     | mod-suc-periodic a b
... | yes _   | yes _   | ih = cong suc ih
... | yes p   | no  ¬p  | ih = ⊥-elim (¬p (subst (λ k → suc k < suc b) ih p))
... | no  ¬p  | yes p   | ih = ⊥-elim (¬p (subst (λ k → suc k < suc b) (sym ih) p))
... | no  _   | no  _   | _  = refl
