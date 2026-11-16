------------------------------------------------------------------------
-- Substrate.Foundation.Nat.Properties.SubMul.PlusMonusCancelL
--
-- Defines: +-∸-cancelˡ
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.Foundation.Nat.Properties.SubMul; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Foundation.Nat.Properties.SubMul.PlusMonusCancelL where

open import Substrate.Foundation.Nat.Monus
open import Substrate.Foundation.Nat.Nat
open import Substrate.Foundation.Nat.Plus
open import Substrate.Foundation.Eq
+-∸-cancelˡ : (a u v : ℕ) → (a ℕ+ u) ∸ (a ℕ+ v) ≡ u ∸ v
+-∸-cancelˡ zero    u v = refl
+-∸-cancelˡ (suc a) u v = +-∸-cancelˡ a u v
