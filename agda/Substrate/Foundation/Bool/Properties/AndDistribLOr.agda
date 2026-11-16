------------------------------------------------------------------------
-- Substrate.Foundation.Bool.Properties.AndDistribLOr
--
-- Defines: ∧-distribˡ-∨
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.Foundation.Bool.Properties; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Foundation.Bool.Properties.AndDistribLOr where

open import Substrate.Foundation.Bool.Bool
open import Substrate.Foundation.Bool.And
open import Substrate.Foundation.Bool.Or
open import Substrate.Foundation.Eq
∧-distribˡ-∨ : (a b c : Bool) → a ∧ (b ∨ c) ≡ (a ∧ b) ∨ (a ∧ c)
∧-distribˡ-∨ true  _ _ = refl
∧-distribˡ-∨ false _ _ = refl
