------------------------------------------------------------------------
-- Substrate.Groups.S4
--
-- The symmetric group S_4 — bijections of the 4-element AXES set.
--
-- Representation choice: a Permutation is a record bundling an
-- apply function, its inverse, and the two inverse-relation proofs.
-- This avoids enumerating 24 explicit constructors AND avoids the
-- 24³ = 13,824 case-analysis associativity proof that a constructor-
-- based encoding would force.
--
-- Equivalence: pointwise equality of the apply function. This is
-- decidable on a finite domain (Axis has 4 elements) and avoids
-- function extensionality.
--
-- Group structure: composition is function composition (and IS
-- associative pointwise), identity is the identity function, inverse
-- is the bundled inverse function.
--
-- See: catalog/cocycles.md § CY-5 — S_4 ≅ V_4 ⋊ S_3 is the primary
-- algebraic foundation; this module is the S_4 half.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Groups.S4 where

open import Level using (0ℓ)
open import Algebra.Bundles using (Group)
open import Algebra.Definitions
open import Algebra.Structures
open import Relation.Binary.PropositionalEquality
  using (_≡_; refl; sym; trans; cong)
open import Relation.Binary.Structures using (IsEquivalence)
open import Data.Product using (_,_)
open import Function.Base using (_∘_; id)

open import Substrate.Axes using (Axis; D; C; S; W)

------------------------------------------------------------------------
-- Permutation = bijection of Axis to itself.
------------------------------------------------------------------------

record Permutation : Set where
  field
    apply  : Axis → Axis
    invₐ   : Axis → Axis
    inv-l  : (x : Axis) → invₐ (apply x) ≡ x
    inv-r  : (x : Axis) → apply (invₐ x) ≡ x

open Permutation public

------------------------------------------------------------------------
-- Pointwise equivalence on Permutations.
------------------------------------------------------------------------

infix 4 _≈_

_≈_ : Permutation → Permutation → Set
σ ≈ τ = (x : Axis) → apply σ x ≡ apply τ x

≈-refl : (σ : Permutation) → σ ≈ σ
≈-refl σ x = refl

≈-sym : {σ τ : Permutation} → σ ≈ τ → τ ≈ σ
≈-sym σ≈τ x = sym (σ≈τ x)

≈-trans : {σ τ ρ : Permutation} → σ ≈ τ → τ ≈ ρ → σ ≈ ρ
≈-trans σ≈τ τ≈ρ x = trans (σ≈τ x) (τ≈ρ x)

≈-isEquivalence : IsEquivalence _≈_
≈-isEquivalence = record
  { refl  = λ {σ}        → ≈-refl σ
  ; sym   = λ {σ} {τ}    → ≈-sym {σ} {τ}
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

-- Identity permutation.
ε : Permutation
ε = record
  { apply = id
  ; invₐ  = id
  ; inv-l = λ _ → refl
  ; inv-r = λ _ → refl
  }

-- Inverse permutation. Swap apply and invₐ.
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
-- function composition is associative pointwise by `refl`, so we
-- don't have to case-analyze 24³ products.
------------------------------------------------------------------------

·-assoc : (σ τ ρ : Permutation) → ((σ · τ) · ρ) ≈ (σ · (τ · ρ))
·-assoc σ τ ρ x = refl   -- (σ ∘ τ ∘ ρ) x = σ (τ (ρ x)) — definitional

ε-left : (σ : Permutation) → (ε · σ) ≈ σ
ε-left σ x = refl

ε-right : (σ : Permutation) → (σ · ε) ≈ σ
ε-right σ x = refl

inv-left : (σ : Permutation) → ((σ ⁻¹) · σ) ≈ ε
inv-left σ x = inv-l σ x

inv-right : (σ : Permutation) → (σ · (σ ⁻¹)) ≈ ε
inv-right σ x = inv-r σ x

------------------------------------------------------------------------
-- Congruence of · and ⁻¹ with respect to ≈.
------------------------------------------------------------------------

·-cong : {σ₁ σ₂ τ₁ τ₂ : Permutation} →
         σ₁ ≈ σ₂ → τ₁ ≈ τ₂ → (σ₁ · τ₁) ≈ (σ₂ · τ₂)
·-cong {σ₁} {σ₂} {τ₁} {τ₂} σ₁≈σ₂ τ₁≈τ₂ x =
  trans (cong (apply σ₁) (τ₁≈τ₂ x))
        (σ₁≈σ₂ (apply τ₂ x))

-- For ⁻¹ to respect ≈ we need: if σ₁ and σ₂ agree on apply, then
-- their invₐ's also agree. This follows from uniqueness of two-sided
-- inverses on bijections.
⁻¹-cong : {σ τ : Permutation} → σ ≈ τ → (σ ⁻¹) ≈ (τ ⁻¹)
⁻¹-cong {σ} {τ} σ≈τ x =
  -- Goal: invₐ σ x ≡ invₐ τ x.
  --
  -- Strategy:
  --   apply τ (invₐ σ x) = apply σ (invₐ σ x)  (since σ ≈ τ)
  --                      = x                    (inv-r σ)
  -- Then applying invₐ τ to both sides and using inv-l τ on the LHS:
  --   invₐ σ x = invₐ τ (apply τ (invₐ σ x))   (sym (inv-l τ ...))
  --            = invₐ τ x                       (cong invₐ τ step)
  let
    step : apply τ (invₐ σ x) ≡ x
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

S₄-Group : Group 0ℓ 0ℓ
S₄-Group = record
  { Carrier = Permutation
  ; _≈_     = _≈_
  ; _∙_     = _·_
  ; ε       = ε
  ; _⁻¹     = _⁻¹
  ; isGroup = isGroup
  }

------------------------------------------------------------------------
-- Notes
--
-- 1. We don't enumerate the 24 elements of S_4 explicitly. The
--    representation as Permutation records captures them implicitly:
--    every distinct (apply, invₐ, inv-l, inv-r) tuple is a distinct
--    S_4 element up to ≈.
--
-- 2. Decidability of ≈ on this representation is straightforward
--    (compare apply on each of the 4 Axes). Not implemented here —
--    deferred to when a downstream theorem needs it.
--
-- 3. To prove |S_4| = 24 we'd construct a bijection between
--    Permutation and Fin 24 (or equivalently, between Permutation
--    and a 24-element enumeration). Also deferred.
--
-- 4. This module is the S_4 half of the catalog's V_4 ⋊ S_3 ≅ S_4
--    identification (M41 v19). The V_4 ⊳ S_4 embedding and
--    normality proof live in Substrate.Groups.V4-Embedding (S8).
------------------------------------------------------------------------
