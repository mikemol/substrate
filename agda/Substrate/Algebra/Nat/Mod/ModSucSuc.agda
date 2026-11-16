------------------------------------------------------------------------
-- Substrate.Algebra.Nat.Mod.ModSucSuc
--
-- Defines: mod-suc-suc
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.Algebra.Nat.Mod; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.Nat.Mod.ModSucSuc where

open import Substrate.Foundation.Nat.Le
open import Substrate.Foundation.Nat.Lt
open import Substrate.Foundation.Nat.Lt2
open import Substrate.Foundation.Nat.Nat
open import Substrate.Foundation.Nat.Properties.Order.LeSucR
open import Substrate.Foundation.Empty.BotElim
open import Substrate.Foundation.Negation.Dec
open import Substrate.Foundation.Negation.Preamble
open import Substrate.Foundation.Nat.Nat.ModSuc
open import Substrate.Algebra.Nat.Mod.ModSucBound
open import Substrate.Algebra.Nat.Mod.ModSucId
open import Substrate.Foundation.Eq
open import Substrate.Foundation.Eq.Cong
open import Substrate.Foundation.Eq.Subst
open import Substrate.Foundation.Eq.Sym



------------------------------------------------------------------------
-- 5. mod-suc-suc — mod commutes with one suc-step (modulo a mod).
--
-- (suc a) mod-suc n ≡ (suc (a mod-suc n)) mod-suc n. Needed by
-- σ-iterate-toℕ for the cyclic-suc HasOrderPerm derivation: lets us
-- thread a `suc` past `mod-suc n` at no cost.
--
-- Both sides expand to a with-clause; we case-split on both
-- discriminants and discharge the impossible cross-cases via
-- mod-suc-id (a mod-suc n) ≡ (a mod-suc n) (idempotence).
------------------------------------------------------------------------

mod-suc-suc : (a n : ℕ) → (suc a) mod-suc n ≡ (suc (a mod-suc n)) mod-suc n
mod-suc-suc a n
  with suc (a mod-suc n) <? suc n
     | suc ((a mod-suc n) mod-suc n) <? suc n
     | mod-suc-id (a mod-suc n) n (mod-suc-bound a n)
... | yes _   | yes _   | aa≡a = cong suc (sym aa≡a)
... | yes p   | no  ¬q  | aa≡a = ⊥-elim (¬q (subst (λ k → suc k < suc n) (sym aa≡a) p))
... | no  ¬p  | yes q   | aa≡a = ⊥-elim (¬p (subst (λ k → suc k < suc n) aa≡a q))
... | no  _   | no  _   | _    = refl
