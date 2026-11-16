------------------------------------------------------------------------
-- Substrate.Foundation.Bool.Properties.AndElimR
--
-- Defines: ∧-elimʳ
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.Foundation.Bool.Properties; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Foundation.Bool.Properties.AndElimR where

open import Substrate.Foundation.Eq
open import Substrate.Foundation.Bool.Bool
open import Substrate.Foundation.Bool.And



∧-elimʳ : {a b : Bool} → (a ∧ b) ≡ true → b ≡ true
∧-elimʳ {true}  h = h
∧-elimʳ {false} ()
