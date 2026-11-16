------------------------------------------------------------------------
-- Substrate.Foundation.Bool.Properties.XorSame
--
-- Defines: xor-same
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.Foundation.Bool.Properties; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Foundation.Bool.Properties.XorSame where

open import Substrate.Foundation.Eq
open import Substrate.Foundation.Bool.Bool
open import Substrate.Foundation.Bool.Xor



xor-same : (b : Bool) → b xor b ≡ false
xor-same true  = refl
xor-same false = refl
