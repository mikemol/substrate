------------------------------------------------------------------------
-- Substrate.Foundation.List
--
-- Substrate-native universe-polymorphic List. Distinguished from
-- Substrate.Groups.Coxeter.Word (mono-universe, named after its
-- Coxeter-presentation role); use this module for general
-- sequence-of-elements types parametric over universe level.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Foundation.List where

open import Substrate.Foundation.Level using (Level)

private
  variable
    ℓ : Level

data List (A : Set ℓ) : Set ℓ where
  []  : List A
  _∷_ : A → List A → List A

infixr 5 _∷_

------------------------------------------------------------------------
-- Basic operations.
------------------------------------------------------------------------

_++_ : {A : Set ℓ} → List A → List A → List A
[]       ++ ys = ys
(x ∷ xs) ++ ys = x ∷ (xs ++ ys)

infixr 5 _++_

-- length: needs ℕ; defer to a separate file to keep this minimal.

------------------------------------------------------------------------
-- foldl / foldr (universe-polymorphic both in element and accumulator).
------------------------------------------------------------------------

foldl : ∀ {ℓ₁ ℓ₂} {A : Set ℓ₁} {B : Set ℓ₂}
      → (B → A → B) → B → List A → B
foldl _ acc []       = acc
foldl f acc (x ∷ xs) = foldl f (f acc x) xs

foldr : ∀ {ℓ₁ ℓ₂} {A : Set ℓ₁} {B : Set ℓ₂}
      → (A → B → B) → B → List A → B
foldr _ acc []       = acc
foldr f acc (x ∷ xs) = f x (foldr f acc xs)
