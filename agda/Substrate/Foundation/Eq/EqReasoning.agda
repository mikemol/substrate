------------------------------------------------------------------------
-- Substrate.Foundation.Eq.EqReasoning
--
-- Defines: ≡-Reasoning
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.Foundation.Eq; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Foundation.Eq.EqReasoning where

open import Substrate.Foundation.Level
private variable a b c : Level
open import Substrate.Foundation.Eq.Preamble
open import Substrate.Foundation.Eq
open import Substrate.Foundation.Eq.Trans



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
