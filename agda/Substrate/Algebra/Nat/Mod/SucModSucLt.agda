------------------------------------------------------------------------
-- Substrate.Algebra.Nat.Mod.SucModSucLt
--
-- Defines: suc-mod-suc-lt
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.Algebra.Nat.Mod; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.Nat.Mod.SucModSucLt where

open import Substrate.Foundation.Nat.Le
open import Substrate.Foundation.Nat.Lt
open import Substrate.Foundation.Nat.Lt2
open import Substrate.Foundation.Nat.Nat
open import Substrate.Foundation.Nat.Properties.Order.LeSucR
open import Substrate.Foundation.Empty.BotElim
open import Substrate.Foundation.Negation.Dec
open import Substrate.Foundation.Negation.Preamble
open import Substrate.Foundation.Nat.Nat.ModSuc
open import Substrate.Algebra.Nat.Mod.ModSucId
open import Substrate.Foundation.Eq



------------------------------------------------------------------------
-- 6. Two specialised mod-suc identities used by Coxeter.Cyclic's
-- insert-canonical proof.
--
--   suc-mod-suc-lt : a < b → (suc a) mod-suc b ≡ suc a
--   suc-mod-suc-self : (suc b) mod-suc b ≡ zero
------------------------------------------------------------------------

suc-mod-suc-lt : (a b : ℕ) → a < b → (suc a) mod-suc b ≡ suc a
suc-mod-suc-lt a b a<b = mod-suc-id (suc a) b (s≤s a<b)
