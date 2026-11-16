------------------------------------------------------------------------
-- Substrate.Foundation.Nat.Properties.Order.LeTight
--
-- Defines: ≤-tight
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.Foundation.Nat.Properties.Order; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Foundation.Nat.Properties.Order.LeTight where

open import Substrate.Foundation.Nat.Le
open import Substrate.Foundation.Nat.Nat
open import Substrate.Foundation.Empty.BotElim
open import Substrate.Foundation.Negation.Not
open import Substrate.Foundation.Negation.Preamble
open import Substrate.Foundation.Eq
open import Substrate.Foundation.Eq.Cong
-- ≤-tight: if suc m ≤ suc b AND ¬ (suc m ≤ b), then m ≡ b.
--
-- Used by DivMod reconstruction: when the mod-suc wraps (the NO
-- branch of `suc (a mod-suc b) <? suc b`), the remainder is exactly b.
------------------------------------------------------------------------


≤-tight : (m b : ℕ) → suc m ≤ suc b → ¬ (suc m ≤ b) → m ≡ b
≤-tight zero    zero    _         _      = refl
≤-tight zero    (suc b) _         ¬sm≤b  = ⊥-elim (¬sm≤b (s≤s z≤n))
≤-tight (suc m) zero    (s≤s ()) _
≤-tight (suc m) (suc b) (s≤s sm≤sb) ¬sm≤b' =
  cong suc (≤-tight m b sm≤sb (λ p → ¬sm≤b' (s≤s p)))
