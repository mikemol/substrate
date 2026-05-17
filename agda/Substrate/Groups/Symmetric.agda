------------------------------------------------------------------------
-- Substrate.Groups.Symmetric
--
-- The symmetric group on an arbitrary carrier (A : Set) — bijections
-- A → A under composition. Module-parameterized over A, so the same
-- machinery instantiates for any carrier (Axis → S₄, Fin n → Sₙ, or
-- anything else).
--
-- Architecture (per [[feedback-v4-typeclass-architecture]]):
-- Substrate.Groups.S4 and Substrate.Groups.SFin are now thin adapters
-- that `open import Substrate.Groups.Symmetric <carrier> public`.
-- ZERO duplication; new symmetric groups over different carriers
-- cost ≤ 3 lines.
--
-- Representation choice: a Permutation is a record bundling apply +
-- invₐ + two inverse-relation proofs. Avoids enumerating n!
-- constructors AND avoids (n!)³ case-analysis for associativity
-- (function composition is associative pointwise by refl).
--
-- Equivalence: pointwise equality of apply.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Groups.Symmetric (A : Set) where

open import Level using (0ℓ)
open import Algebra.Bundles using (Group)
open import Algebra.Definitions
open import Algebra.Structures
open import Relation.Binary.PropositionalEquality
  using (_≡_; refl; sym; trans; cong)
open import Relation.Binary.Structures using (IsEquivalence)
open import Data.Product using (_,_)
open import Function.Base using (_∘_; id)

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
-- Pointwise equivalence on Permutations.
------------------------------------------------------------------------

infix 4 _≈_

_≈_ : Permutation → Permutation → Set
σ ≈ τ = (x : A) → apply σ x ≡ apply τ x

≈-refl : (σ : Permutation) → σ ≈ σ
≈-refl σ x = refl

≈-sym : {σ τ : Permutation} → σ ≈ τ → τ ≈ σ
≈-sym σ≈τ x = sym (σ≈τ x)

≈-trans : {σ τ ρ : Permutation} → σ ≈ τ → τ ≈ ρ → σ ≈ ρ
≈-trans σ≈τ τ≈ρ x = trans (σ≈τ x) (τ≈ρ x)

≈-isEquivalence : IsEquivalence _≈_
≈-isEquivalence = record
  { refl  = λ {σ}         → ≈-refl σ
  ; sym   = λ {σ} {τ}     → ≈-sym {σ} {τ}
  ; trans = λ {σ} {τ} {ρ} → ≈-trans {σ} {τ} {ρ}
  }

------------------------------------------------------------------------
-- Group operations.
------------------------------------------------------------------------

-- Composition. (σ · τ)(x) = σ(τ(x)).
_·_ : Permutation → Permutation → Permutation
σ · τ = record
  { apply = λ x → apply σ (apply τ x)
  ; invₐ  = λ x → invₐ τ (invₐ σ x)
  ; inv-l = λ x →
      trans (cong (invₐ τ) (inv-l σ (apply τ x))) (inv-l τ x)
  ; inv-r = λ x →
      trans (cong (apply σ) (inv-r τ (invₐ σ x))) (inv-r σ x)
  }

-- Identity.
ε : Permutation
ε = record
  { apply = id
  ; invₐ  = id
  ; inv-l = λ _ → refl
  ; inv-r = λ _ → refl
  }

-- Inverse. Swap apply and invₐ.
_⁻¹ : Permutation → Permutation
σ ⁻¹ = record
  { apply = invₐ σ
  ; invₐ  = apply σ
  ; inv-l = inv-r σ
  ; inv-r = inv-l σ
  }

------------------------------------------------------------------------
-- Group axioms, proved up to pointwise equivalence.
--
-- Associativity is the load-bearing reason for this representation:
-- function composition is associative pointwise by `refl`.
------------------------------------------------------------------------

·-assoc : (σ τ ρ : Permutation) → ((σ · τ) · ρ) ≈ (σ · (τ · ρ))
·-assoc σ τ ρ x = refl

ε-left : (σ : Permutation) → (ε · σ) ≈ σ
ε-left σ x = refl

ε-right : (σ : Permutation) → (σ · ε) ≈ σ
ε-right σ x = refl

inv-left : (σ : Permutation) → ((σ ⁻¹) · σ) ≈ ε
inv-left σ x = inv-l σ x

inv-right : (σ : Permutation) → (σ · (σ ⁻¹)) ≈ ε
inv-right σ x = inv-r σ x

------------------------------------------------------------------------
-- Congruence of · and ⁻¹.
------------------------------------------------------------------------

·-cong : {σ₁ σ₂ τ₁ τ₂ : Permutation} →
         σ₁ ≈ σ₂ → τ₁ ≈ τ₂ → (σ₁ · τ₁) ≈ (σ₂ · τ₂)
·-cong {σ₁} {σ₂} {τ₁} {τ₂} σ₁≈σ₂ τ₁≈τ₂ x =
  trans (cong (apply σ₁) (τ₁≈τ₂ x))
        (σ₁≈σ₂ (apply τ₂ x))

⁻¹-cong : {σ τ : Permutation} → σ ≈ τ → (σ ⁻¹) ≈ (τ ⁻¹)
⁻¹-cong {σ} {τ} σ≈τ x =
  let step : apply τ (invₐ σ x) ≡ x
      step = trans (sym (σ≈τ (invₐ σ x))) (inv-r σ x)
  in trans (sym (inv-l τ (invₐ σ x))) (cong (invₐ τ) step)

------------------------------------------------------------------------
-- Bundle as a Group (stdlib).
------------------------------------------------------------------------

isMagma : IsMagma _≈_ _·_
isMagma = record
  { isEquivalence = ≈-isEquivalence
  ; ∙-cong        = λ {σ₁} {σ₂} {τ₁} {τ₂} → ·-cong {σ₁} {σ₂} {τ₁} {τ₂}
  }

isSemigroup : IsSemigroup _≈_ _·_
isSemigroup = record
  { isMagma = isMagma
  ; assoc   = ·-assoc
  }

isMonoid : IsMonoid _≈_ _·_ ε
isMonoid = record
  { isSemigroup = isSemigroup
  ; identity    = ε-left , ε-right
  }

isGroup : IsGroup _≈_ _·_ ε _⁻¹
isGroup = record
  { isMonoid = isMonoid
  ; inverse  = inv-left , inv-right
  ; ⁻¹-cong  = λ {σ} {τ} → ⁻¹-cong {σ} {τ}
  }

Symmetric-Group : Group 0ℓ 0ℓ
Symmetric-Group = record
  { Carrier = Permutation
  ; _≈_     = _≈_
  ; _∙_     = _·_
  ; ε       = ε
  ; _⁻¹     = _⁻¹
  ; isGroup = isGroup
  }

------------------------------------------------------------------------
-- Injectivity of apply (derived from the bijection certificate).
------------------------------------------------------------------------

σ-injective : (σ : Permutation) (x y : A) →
              apply σ x ≡ apply σ y → x ≡ y
σ-injective σ x y eq =
  trans (sym (inv-l σ x))
        (trans (cong (invₐ σ) eq) (inv-l σ y))
