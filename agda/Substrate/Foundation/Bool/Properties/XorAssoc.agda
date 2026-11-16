------------------------------------------------------------------------
-- Substrate.Foundation.Bool.Properties.XorAssoc
--
-- Defines: xor-assoc
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.Foundation.Bool.Properties; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Foundation.Bool.Properties.XorAssoc where

open import Substrate.Foundation.Eq
open import Substrate.Foundation.Bool.Bool
open import Substrate.Foundation.Bool.Xor



xor-assoc : (a b c : Bool) → (a xor b) xor c ≡ a xor (b xor c)
xor-assoc true  true  true  = refl
xor-assoc true  true  false = refl
xor-assoc true  false true  = refl
xor-assoc true  false false = refl
xor-assoc false true  true  = refl
xor-assoc false true  false = refl
xor-assoc false false true  = refl
xor-assoc false false false = refl
