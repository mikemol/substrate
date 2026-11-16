------------------------------------------------------------------------
-- Substrate.Foundation.Bool.Properties.AndAssoc
--
-- Defines: ∧-assoc
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.Foundation.Bool.Properties; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Foundation.Bool.Properties.AndAssoc where

open import Substrate.Foundation.Eq
open import Substrate.Foundation.Bool.Bool
open import Substrate.Foundation.Bool.And



∧-assoc : (a b c : Bool) → (a ∧ b) ∧ c ≡ a ∧ (b ∧ c)
∧-assoc true  b c = refl
∧-assoc false b c = refl
