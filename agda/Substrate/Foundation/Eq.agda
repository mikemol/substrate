------------------------------------------------------------------------
-- Substrate.Foundation.Eq
--
-- Substrate-native propositional equality. Phase 2: native datatype +
-- BUILTIN EQUALITY + standard combinators, level-polymorphic.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Foundation.Eq where

open import Substrate.Foundation.Empty using (⊥)
open import Substrate.Foundation.Level using (Level; _⊔_)

private variable
  a b c : Level

infix 4 _≡_ _≢_

data _≡_ {A : Set a} (x : A) : A → Set a where
  refl : x ≡ x

{-# BUILTIN EQUALITY _≡_ #-}

_≢_ : {A : Set a} → A → A → Set a
x ≢ y = x ≡ y → ⊥

sym : {A : Set a} {x y : A} → x ≡ y → y ≡ x
sym refl = refl

trans : {A : Set a} {x y z : A} → x ≡ y → y ≡ z → x ≡ z
trans refl q = q

cong : {A : Set a} {B : Set b} (f : A → B) {x y : A} → x ≡ y → f x ≡ f y
cong f refl = refl

cong₂ : {A : Set a} {B : Set b} {C : Set c} (f : A → B → C) {x y : A} {u v : B} →
        x ≡ y → u ≡ v → f x u ≡ f y v
cong₂ f refl refl = refl

subst : {A : Set a} (P : A → Set b) {x y : A} → x ≡ y → P x → P y
subst _ refl p = p

------------------------------------------------------------------------
-- Equational-reasoning syntax.
------------------------------------------------------------------------

module ≡-Reasoning {a : Level} where
  infix  3 _∎
  infixr 2 _≡⟨_⟩_ _≡⟨⟩_
  infix  1 begin_

  begin_ : {A : Set a} {x y : A} → x ≡ y → x ≡ y
  begin_ p = p

  _≡⟨_⟩_ : {A : Set a} (x : A) {y z : A} → x ≡ y → y ≡ z → x ≡ z
  _ ≡⟨ p ⟩ q = trans p q

  _≡⟨⟩_ : {A : Set a} (x : A) {y : A} → x ≡ y → x ≡ y
  _ ≡⟨⟩ q = q

  _∎ : {A : Set a} (x : A) → x ≡ x
  _ ∎ = refl
