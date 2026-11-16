------------------------------------------------------------------------
-- Substrate.Foundation.Bool.Properties.XorIdentityL
--
-- Defines: xor-identityˡ
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.Foundation.Bool.Properties; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Foundation.Bool.Properties.XorIdentityL where

open import Substrate.Foundation.Bool.Bool
open import Substrate.Foundation.Bool.Xor
open import Substrate.Foundation.Eq
-- xor lemmas (case-analytical proofs).
------------------------------------------------------------------------

xor-identityˡ : (b : Bool) → false xor b ≡ b
xor-identityˡ true  = refl
xor-identityˡ false = refl
