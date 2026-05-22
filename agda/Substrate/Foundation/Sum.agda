------------------------------------------------------------------------
-- Substrate.Foundation.Sum
--
-- Substrate-native disjoint sum. Phase 2: native datatype + eliminator.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Foundation.Sum where

infixr 1 _⊎_

data _⊎_ (A B : Set) : Set where
  inj₁ : A → A ⊎ B
  inj₂ : B → A ⊎ B

[_,_] : {A B C : Set} → (A → C) → (B → C) → A ⊎ B → C
[ f , g ] (inj₁ a) = f a
[ f , g ] (inj₂ b) = g b

-- Strict variant; identical to [_,_] in the substrate-native form.
[_,_]′ : {A B C : Set} → (A → C) → (B → C) → A ⊎ B → C
[_,_]′ = [_,_]
