------------------------------------------------------------------------
-- Substrate.Foundation.Bool.Properties.OrIdentityR
--
-- Defines: ∨-identityʳ
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.Foundation.Bool.Properties; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Foundation.Bool.Properties.OrIdentityR where

open import Substrate.Foundation.Eq
open import Substrate.Foundation.Bool.Bool
open import Substrate.Foundation.Bool.Or



∨-identityʳ : (a : Bool) → a ∨ false ≡ a
∨-identityʳ true  = refl
∨-identityʳ false = refl
