------------------------------------------------------------------------
-- Substrate.Foundation.Bool.Properties.AndZeroL
--
-- Defines: ∧-zeroˡ
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.Foundation.Bool.Properties; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Foundation.Bool.Properties.AndZeroL where

open import Substrate.Foundation.Bool.Bool
open import Substrate.Foundation.Bool.And
open import Substrate.Foundation.Eq
∧-zeroˡ : (a : Bool) → false ∧ a ≡ false
∧-zeroˡ _ = refl
