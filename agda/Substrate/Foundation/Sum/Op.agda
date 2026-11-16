------------------------------------------------------------------------
-- Substrate.Foundation.Sum.Op
--
-- Defines: [_,_]
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.Foundation.Sum; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Foundation.Sum.Op where

open import Substrate.Foundation.Sum.Private
open import Substrate.Foundation.Sum.Sum



[_,_] : {A : Set ℓ₁} {B : Set ℓ₂} {C : Set ℓ₃}
      → (A → C) → (B → C) → A ⊎ B → C
[ f , g ] (inj₁ a) = f a
[ f , g ] (inj₂ b) = g b
