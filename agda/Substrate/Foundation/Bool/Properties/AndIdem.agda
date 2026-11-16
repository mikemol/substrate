------------------------------------------------------------------------
-- Substrate.Foundation.Bool.Properties.AndIdem
--
-- Defines: ∧-idem
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.Foundation.Bool.Properties; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Foundation.Bool.Properties.AndIdem where

open import Substrate.Foundation.Eq
open import Substrate.Foundation.Bool.Bool
open import Substrate.Foundation.Bool.And



∧-idem : (a : Bool) → a ∧ a ≡ a
∧-idem true  = refl
∧-idem false = refl
