------------------------------------------------------------------------
-- Substrate.Foundation.Bool.Properties.AndIdentityR
--
-- Defines: ∧-identityʳ
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.Foundation.Bool.Properties; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Foundation.Bool.Properties.AndIdentityR where

open import Substrate.Foundation.Eq
open import Substrate.Foundation.Bool.Bool
open import Substrate.Foundation.Bool.And



∧-identityʳ : (a : Bool) → a ∧ true ≡ a
∧-identityʳ true  = refl
∧-identityʳ false = refl
