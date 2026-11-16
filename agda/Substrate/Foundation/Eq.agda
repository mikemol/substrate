------------------------------------------------------------------------
-- Substrate.Foundation.Eq.Eq
--
-- Defines: _≡_, refl
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.Foundation.Eq; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Foundation.Eq where

open import Substrate.Foundation.Level
private variable a b c : Level
open import Substrate.Foundation.Eq.Preamble

infix 4 _≡_


data _≡_ {A : Set a} (x : A) : A → Set a where
  refl : x ≡ x

{-# BUILTIN EQUALITY _≡_ #-}
