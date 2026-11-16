------------------------------------------------------------------------
-- Substrate.Foundation.Bool.Properties.XorComm
--
-- Defines: xor-comm
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.Foundation.Bool.Properties; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Foundation.Bool.Properties.XorComm where

open import Substrate.Foundation.Eq
open import Substrate.Foundation.Bool.Bool
open import Substrate.Foundation.Bool.Xor



xor-comm : (a b : Bool) → a xor b ≡ b xor a
xor-comm true  true  = refl
xor-comm true  false = refl
xor-comm false true  = refl
xor-comm false false = refl
