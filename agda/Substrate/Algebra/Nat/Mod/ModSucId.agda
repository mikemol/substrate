------------------------------------------------------------------------
-- Substrate.Algebra.Nat.Mod.ModSucId
--
-- Defines: mod-suc-id
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.Algebra.Nat.Mod; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.Nat.Mod.ModSucId where

open import Substrate.Foundation.Nat.Le
open import Substrate.Foundation.Nat.Lt
open import Substrate.Foundation.Nat.Lt2
open import Substrate.Foundation.Nat.Nat
open import Substrate.Foundation.Nat.Properties.Order.LeSucR
open import Substrate.Foundation.Empty.BotElim
open import Substrate.Foundation.Negation.Dec
open import Substrate.Foundation.Negation.Preamble
open import Substrate.Foundation.Nat.Nat.ModSuc
open import Substrate.Foundation.Eq
open import Substrate.Foundation.Eq.Cong
open import Substrate.Foundation.Eq.Subst
open import Substrate.Foundation.Eq.Sym



------------------------------------------------------------------------
-- 3. mod-suc-id — mod fixes elements below the modulus.
--
-- For a < suc b, a mod-suc b ≡ a (no wrap occurs). Proof by induction
-- on a, dispatching on the same with-clause that defines _mod-suc_.
-- The `no` branch is impossible by the bound; we discharge it via
-- the IH transported through the comparison.
------------------------------------------------------------------------

mod-suc-id : (a b : ℕ) → a < suc b → a mod-suc b ≡ a
mod-suc-id zero    _ _         = refl
mod-suc-id (suc a) b (s≤s a≤b) with suc (a mod-suc b) <? suc b
                                  | mod-suc-id a b (≤-suc-r a≤b)
... | yes _    | ih = cong suc ih
... | no  ¬lt  | ih =
  ⊥-elim (¬lt (subst (λ k → suc k < suc b) (sym ih) (s≤s a≤b)))
