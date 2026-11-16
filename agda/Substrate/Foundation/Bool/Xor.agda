------------------------------------------------------------------------
-- Substrate.Foundation.Bool.Xor
--
-- Defines: _xor_
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.Foundation.Bool; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Foundation.Bool.Xor where

open import Substrate.Foundation.Bool.Bool
open import Substrate.Foundation.Bool.Not

infixr 5 _xor_


_xor_ : Bool → Bool → Bool
true  xor b = not b
false xor b = b
