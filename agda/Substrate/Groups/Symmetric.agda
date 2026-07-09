------------------------------------------------------------------------
-- Substrate.Groups.Symmetric
--
-- The symmetric group on an arbitrary carrier (A : Set) — bijections
-- A → A under composition. Module-parameterized over A.
--
-- Substrate-native: no stdlib imports. Uses Substrate.Algebra.SetoidGroup
-- as the bundled type and Substrate.Foundation.* for primitives.
--
-- Representation: a Permutation is a record bundling apply + invₐ +
-- two inverse-relation proofs. Equivalence: pointwise equality of
-- apply.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Groups.Symmetric (A : Set) where

open import Substrate.Foundation.Eq
  using (_≡_; refl; sym; trans; cong; cong-trans; sym-trans)
open import Substrate.Foundation.Function
  using (id)
open import Substrate.Algebra.SetoidGroup using (SetoidGroup)

------------------------------------------------------------------------
-- Permutation = bijection of A to itself.
------------------------------------------------------------------------

record Permutation : Set where
  field
    apply  : A → A
    invₐ   : A → A
    inv-l  : (x : A) → invₐ (apply x) ≡ x
    inv-r  : (x : A) → apply (invₐ x) ≡ x

open Permutation public

------------------------------------------------------------------------
-- Pointwise equivalence.
------------------------------------------------------------------------

infix 4 _≈_

_≈_ : Permutation → Permutation → Set
σ ≈ τ = (x : A) → apply σ x ≡ apply τ x

≈-refl : (σ : Permutation) → σ ≈ σ
≈-refl _ _ = refl

≈-sym : {σ τ : Permutation} → σ ≈ τ → τ ≈ σ
≈-sym σ≈τ x = sym (σ≈τ x)

≈-trans : {σ τ ρ : Permutation} → σ ≈ τ → τ ≈ ρ → σ ≈ ρ
≈-trans σ≈τ τ≈ρ x = trans (σ≈τ x) (τ≈ρ x)

------------------------------------------------------------------------
-- Group operations.
------------------------------------------------------------------------

_·_ : Permutation → Permutation → Permutation
σ · τ = record
  { apply = λ x → apply σ (apply τ x)
  ; invₐ  = λ x → invₐ τ (invₐ σ x)
  ; inv-l = λ x →
      cong-trans (invₐ τ) (inv-l σ (apply τ x)) (inv-l τ x)
  ; inv-r = λ x →
      cong-trans (apply σ) (inv-r τ (invₐ σ x)) (inv-r σ x)
  }

ε : Permutation
ε = record
  { apply = id
  ; invₐ  = id
  ; inv-l = λ _ → refl
  ; inv-r = λ _ → refl
  }

_⁻¹ : Permutation → Permutation
σ ⁻¹ = record
  { apply = invₐ σ
  ; invₐ  = apply σ
  ; inv-l = inv-r σ
  ; inv-r = inv-l σ
  }

------------------------------------------------------------------------
-- Group axioms (up to ≈). Pointwise function-composition associativity
-- is `refl` on each x.
------------------------------------------------------------------------

·-assoc : (σ τ ρ : Permutation) → ((σ · τ) · ρ) ≈ (σ · (τ · ρ))
·-assoc _ _ _ _ = refl

ε-left : (σ : Permutation) → (ε · σ) ≈ σ
ε-left _ _ = refl

ε-right : (σ : Permutation) → (σ · ε) ≈ σ
ε-right _ _ = refl

inv-left : (σ : Permutation) → ((σ ⁻¹) · σ) ≈ ε
inv-left σ x = inv-l σ x

inv-right : (σ : Permutation) → (σ · (σ ⁻¹)) ≈ ε
inv-right σ x = inv-r σ x

------------------------------------------------------------------------
-- Congruences.
------------------------------------------------------------------------

·-cong :
  {σ₁ σ₂ τ₁ τ₂ : Permutation} →
  σ₁ ≈ σ₂ → τ₁ ≈ τ₂ → (σ₁ · τ₁) ≈ (σ₂ · τ₂)
·-cong {σ₁} {σ₂} {τ₁} {τ₂} σ₁≈σ₂ τ₁≈τ₂ x =
  cong-trans (apply σ₁) (τ₁≈τ₂ x)
             (σ₁≈σ₂ (apply τ₂ x))

⁻¹-cong :
  {σ τ : Permutation} → σ ≈ τ → (σ ⁻¹) ≈ (τ ⁻¹)
⁻¹-cong {σ} {τ} σ≈τ x =
  let step : apply τ (invₐ σ x) ≡ x
      step = sym-trans (σ≈τ (invₐ σ x)) (inv-r σ x)
  in sym-trans (inv-l τ (invₐ σ x)) (cong (invₐ τ) step)

------------------------------------------------------------------------
-- Bundle as a substrate-native SetoidGroup.
------------------------------------------------------------------------

Symmetric-Group : SetoidGroup Permutation _≈_
Symmetric-Group = record
  { _∙_       = _·_
  ; ε         = ε
  ; _⁻¹       = _⁻¹
  ; ≈-refl    = ≈-refl
  ; ≈-sym     = λ {σ} {τ} → ≈-sym {σ} {τ}
  ; ≈-trans   = λ {σ} {τ} {ρ} → ≈-trans {σ} {τ} {ρ}
  ; ∙-assoc   = ·-assoc
  ; ε-left    = ε-left
  ; ε-right   = ε-right
  ; inv-left  = inv-left
  ; inv-right = inv-right
  ; ∙-cong    = λ {σ₁} {σ₂} {τ₁} {τ₂} → ·-cong {σ₁} {σ₂} {τ₁} {τ₂}
  ; ⁻¹-cong   = λ {σ} {τ} → ⁻¹-cong {σ} {τ}
  }

------------------------------------------------------------------------
-- Injectivity of apply.
------------------------------------------------------------------------

σ-injective :
  (σ : Permutation) (x y : A) → apply σ x ≡ apply σ y → x ≡ y
σ-injective σ x y eq =
  sym-trans (inv-l σ x)
            (cong-trans (invₐ σ) eq (inv-l σ y))
