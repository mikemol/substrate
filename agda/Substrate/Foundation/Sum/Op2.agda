------------------------------------------------------------------------
-- Substrate.Foundation.Sum.Op2
--
-- Defines: [_,_]′
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.Foundation.Sum; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Foundation.Sum.Op2 where

open import Substrate.Foundation.Sum.Private
open import Substrate.Foundation.Sum.Sum
open import Substrate.Foundation.Sum.Op



-- Strict variant; identical to [_,_] in the substrate-native form.
[_,_]′ : {A : Set ℓ₁} {B : Set ℓ₂} {C : Set ℓ₃}
       → (A → C) → (B → C) → A ⊎ B → C
[_,_]′ = [_,_]
