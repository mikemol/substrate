------------------------------------------------------------------------
-- Substrate.Foundation.Bool.Properties.XorIdentityR
--
-- Defines: xor-identityʳ
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.Foundation.Bool.Properties; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Foundation.Bool.Properties.XorIdentityR where

open import Substrate.Foundation.Eq
open import Substrate.Foundation.Bool.Bool
open import Substrate.Foundation.Bool.Xor



xor-identityʳ : (b : Bool) → b xor false ≡ b
xor-identityʳ true  = refl
xor-identityʳ false = refl
