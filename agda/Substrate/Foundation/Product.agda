------------------------------------------------------------------------
-- Substrate.Foundation.Product
--
-- Substrate-native Σ / product. Phase 2: native record, level-poly.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Foundation.Product where

open import Substrate.Foundation.Level using (Level; _⊔_)

private variable
  a b : Level

------------------------------------------------------------------------
-- The Σ record (level-polymorphic).
------------------------------------------------------------------------

infixr 4 _,_
infix  2 Σ-syntax ∃-syntax
infixr 2 _×_

record Σ (A : Set a) (B : A → Set b) : Set (a ⊔ b) where
  constructor _,_
  field
    proj₁ : A
    proj₂ : B proj₁

open Σ public

------------------------------------------------------------------------
-- Σ syntax.
------------------------------------------------------------------------

Σ-syntax : (A : Set a) → (A → Set b) → Set (a ⊔ b)
Σ-syntax A B = Σ A B

syntax Σ-syntax A (λ x → B) = Σ[ x ∈ A ] B

------------------------------------------------------------------------
-- Non-dependent product.
------------------------------------------------------------------------

_×_ : Set a → Set b → Set (a ⊔ b)
A × B = Σ A (λ _ → B)

------------------------------------------------------------------------
-- Existential.
------------------------------------------------------------------------

∃ : {A : Set a} (B : A → Set b) → Set (a ⊔ b)
∃ {A = A} B = Σ A B

∃-syntax : {A : Set a} (B : A → Set b) → Set (a ⊔ b)
∃-syntax = ∃

syntax ∃-syntax (λ x → B) = ∃[ x ] B

------------------------------------------------------------------------
-- -,_ : leave the carrier inferred.
------------------------------------------------------------------------

-,_ : {A : Set a} {B : A → Set b} {x : A} → B x → Σ A B
-,_ {x = x} b = x , b

------------------------------------------------------------------------
-- Σ-equality combinator: build a Σ-equality from component equalities.
-- Substrate-native replacement for stdlib's Data.Product.Properties.Σ-≡,≡→≡.
------------------------------------------------------------------------

open import Substrate.Foundation.Eq using (_≡_; refl; subst)

Σ-≡,≡→≡ :
  {A : Set a} {B : A → Set b}
  {p q : Σ A B} →
  Σ (proj₁ p ≡ proj₁ q)
    (λ eq → subst B eq (proj₂ p) ≡ proj₂ q) →
  p ≡ q
Σ-≡,≡→≡ {p = a , b} {q = .a , .b} (refl , refl) = refl
