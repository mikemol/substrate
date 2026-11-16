------------------------------------------------------------------------
-- Substrate.Foundation.Bool.Properties.AndZeroR
--
-- Defines: ∧-zeroʳ
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.Foundation.Bool.Properties; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Foundation.Bool.Properties.AndZeroR where

open import Substrate.Foundation.Eq
open import Substrate.Foundation.Bool.Bool
open import Substrate.Foundation.Bool.And



∧-zeroʳ : (a : Bool) → a ∧ false ≡ false
∧-zeroʳ true  = refl
∧-zeroʳ false = refl
