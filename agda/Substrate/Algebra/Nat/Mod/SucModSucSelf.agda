------------------------------------------------------------------------
-- Substrate.Algebra.Nat.Mod.SucModSucSelf
--
-- Defines: suc-mod-suc-self
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.Algebra.Nat.Mod; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.Nat.Mod.SucModSucSelf where

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
open import Substrate.Algebra.Nat.Mod.ModSucPeriodic
open import Substrate.Algebra.Nat.Mod.ModSucSuc
open import Substrate.Algebra.Nat.Mod.SucModSucLt
open import Substrate.Foundation.Eq
open import Substrate.Foundation.Eq.Subst



suc-mod-suc-self : (b : ℕ) → (suc b) mod-suc b ≡ zero
suc-mod-suc-self b
  with suc (b mod-suc b) <? suc b
     | mod-suc-id b b (<-suc-self b)
... | yes p≡  | bmodb≡b =
  ⊥-elim (<-irrefl b (subst (λ k → suc k ≤ b) bmodb≡b (s≤s-strip p≡)))
  where
    s≤s-strip : ∀ {m k} → suc m < suc k → m < k
    s≤s-strip (s≤s p) = p
... | no  _   | _ = refl

------------------------------------------------------------------------
-- 7. Capstone.
--
-- Substrate-native `_mod-suc_` ℕ+ bound ℕ+ mod-suc-id ℕ+ mod-suc-periodic
-- ℕ+ mod-suc-suc ℕ+ suc-mod-suc-lt / suc-mod-suc-self. Downstream:
-- cyclic-suc on Fin (suc n) ℕ+ HasOrderPerm
-- (Substrate.Algebra.F2.Linear.FromImages.Permutation.Cyclic) ℕ+
-- Substrate.Groups.Coxeter.Cyclic (insert-canonical bridge).
------------------------------------------------------------------------
