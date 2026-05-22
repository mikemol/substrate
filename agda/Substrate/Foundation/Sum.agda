------------------------------------------------------------------------
-- Substrate.Foundation.Sum
--
-- Substrate-native disjoint sum. Universe-polymorphic; mono-universe
-- usages continue to work via inference at ℓ = lzero.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Foundation.Sum where

open import Substrate.Foundation.Level using (Level; _⊔_)

private
  variable
    ℓ₁ ℓ₂ ℓ₃ : Level

infixr 1 _⊎_

data _⊎_ (A : Set ℓ₁) (B : Set ℓ₂) : Set (ℓ₁ ⊔ ℓ₂) where
  inj₁ : A → A ⊎ B
  inj₂ : B → A ⊎ B

[_,_] : {A : Set ℓ₁} {B : Set ℓ₂} {C : Set ℓ₃}
      → (A → C) → (B → C) → A ⊎ B → C
[ f , g ] (inj₁ a) = f a
[ f , g ] (inj₂ b) = g b

-- Strict variant; identical to [_,_] in the substrate-native form.
[_,_]′ : {A : Set ℓ₁} {B : Set ℓ₂} {C : Set ℓ₃}
       → (A → C) → (B → C) → A ⊎ B → C
[_,_]′ = [_,_]
