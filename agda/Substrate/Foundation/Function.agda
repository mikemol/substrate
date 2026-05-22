------------------------------------------------------------------------
-- Substrate.Foundation.Function
--
-- Substrate-native function combinators. Phase 2: native definitions.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Foundation.Function where

open import Substrate.Foundation.Level using (Level)

private variable
  a b c : Level

infixr 9 _∘_
infixr -1 _$_

id : {A : Set a} → A → A
id x = x

const : {A : Set a} {B : Set b} → A → B → A
const x _ = x

-- Dependent composition: B may depend on A's input.
_∘_ : {A : Set a} {B : A → Set b} {C : {x : A} → B x → Set c} →
      ({x : A} → (y : B x) → C y) →
      (f : (x : A) → B x) →
      (x : A) → C (f x)
(g ∘ f) x = g (f x)

flip : {A : Set a} {B : Set b} {C : A → B → Set c} →
       ((x : A) (y : B) → C x y) → (y : B) (x : A) → C x y
flip f y x = f x y

_$_ : {A : Set a} {B : A → Set b} → ((x : A) → B x) → (x : A) → B x
f $ x = f x

_∋_ : (A : Set a) → A → A
_ ∋ x = x

case_of_ : {A : Set a} {B : A → Set b} (x : A) → ((y : A) → B y) → B x
case x of f = f x
