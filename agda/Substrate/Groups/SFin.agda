------------------------------------------------------------------------
-- Substrate.Groups.SFin
--
-- The parameterised symmetric group S_n on Fin n — bijections of an
-- n-element set. Mirrors Substrate.Groups.S4 with the carrier
-- abstracted from a fixed 4-element Axis to Fin n.
--
-- Representation choice: same as S4 — a Permutation is a record
-- bundling apply + invₐ + two inverse-relation proofs. This avoids
-- enumerating n! explicit constructors AND avoids the (n!)³ case-
-- analysis associativity proof a constructor-based encoding forces.
--
-- Equivalence: pointwise equality of apply. Decidable on Fin n for
-- any n (finite domain), but we don't construct the decision procedure
-- here — deferred until a downstream theorem needs it.
--
-- See: catalog/cocycles.md § CY-2 — this is the symmetric group
--      acting on the variable space V for the K-rule cocycle.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Groups.SFin where

open import Level using (0ℓ)
open import Algebra.Bundles using (Group)
open import Algebra.Structures
open import Relation.Binary.PropositionalEquality
  using (_≡_; refl; sym; trans; cong)
open import Relation.Binary.Structures using (IsEquivalence)
open import Data.Nat using (ℕ)
open import Data.Fin using (Fin)
open import Data.Product using (_,_)
open import Function.Base using (_∘_; id)

------------------------------------------------------------------------
-- Permutation n = bijection Fin n → Fin n.
------------------------------------------------------------------------

record Permutation (n : ℕ) : Set where
  field
    apply  : Fin n → Fin n
    invₐ   : Fin n → Fin n
    inv-l  : (x : Fin n) → invₐ (apply x) ≡ x
    inv-r  : (x : Fin n) → apply (invₐ x) ≡ x

open Permutation public

------------------------------------------------------------------------
-- Everything below is parametric in n.
------------------------------------------------------------------------

module _ {n : ℕ} where

  ----------------------------------------------------------------------
  -- Pointwise equivalence on Permutations.
  ----------------------------------------------------------------------

  infix 4 _≈_

  _≈_ : Permutation n → Permutation n → Set
  σ ≈ τ = (x : Fin n) → apply σ x ≡ apply τ x

  ≈-refl : (σ : Permutation n) → σ ≈ σ
  ≈-refl σ x = refl

  ≈-sym : {σ τ : Permutation n} → σ ≈ τ → τ ≈ σ
  ≈-sym σ≈τ x = sym (σ≈τ x)

  ≈-trans : {σ τ ρ : Permutation n} → σ ≈ τ → τ ≈ ρ → σ ≈ ρ
  ≈-trans σ≈τ τ≈ρ x = trans (σ≈τ x) (τ≈ρ x)

  ≈-isEquivalence : IsEquivalence _≈_
  ≈-isEquivalence = record
    { refl  = λ {σ}         → ≈-refl σ
    ; sym   = λ {σ} {τ}     → ≈-sym {σ} {τ}
    ; trans = λ {σ} {τ} {ρ} → ≈-trans {σ} {τ} {ρ}
    }

  ----------------------------------------------------------------------
  -- Group operations.
  ----------------------------------------------------------------------

  -- Composition. (σ · τ)(x) = σ(τ(x)).
  _·_ : Permutation n → Permutation n → Permutation n
  σ · τ = record
    { apply = λ x → apply σ (apply τ x)
    ; invₐ  = λ x → invₐ τ (invₐ σ x)
    ; inv-l = λ x →
        trans (cong (invₐ τ) (inv-l σ (apply τ x))) (inv-l τ x)
    ; inv-r = λ x →
        trans (cong (apply σ) (inv-r τ (invₐ σ x))) (inv-r σ x)
    }

  -- Identity.
  ε : Permutation n
  ε = record
    { apply = id
    ; invₐ  = id
    ; inv-l = λ _ → refl
    ; inv-r = λ _ → refl
    }

  -- Inverse. Swap apply and invₐ.
  _⁻¹ : Permutation n → Permutation n
  σ ⁻¹ = record
    { apply = invₐ σ
    ; invₐ  = apply σ
    ; inv-l = inv-r σ
    ; inv-r = inv-l σ
    }

  ----------------------------------------------------------------------
  -- Group axioms up to pointwise equivalence.
  ----------------------------------------------------------------------

  ·-assoc : (σ τ ρ : Permutation n) → ((σ · τ) · ρ) ≈ (σ · (τ · ρ))
  ·-assoc σ τ ρ x = refl

  ε-left : (σ : Permutation n) → (ε · σ) ≈ σ
  ε-left σ x = refl

  ε-right : (σ : Permutation n) → (σ · ε) ≈ σ
  ε-right σ x = refl

  inv-left : (σ : Permutation n) → ((σ ⁻¹) · σ) ≈ ε
  inv-left σ x = inv-l σ x

  inv-right : (σ : Permutation n) → (σ · (σ ⁻¹)) ≈ ε
  inv-right σ x = inv-r σ x

  ----------------------------------------------------------------------
  -- Congruence of · and ⁻¹.
  ----------------------------------------------------------------------

  ·-cong : {σ₁ σ₂ τ₁ τ₂ : Permutation n} →
           σ₁ ≈ σ₂ → τ₁ ≈ τ₂ → (σ₁ · τ₁) ≈ (σ₂ · τ₂)
  ·-cong {σ₁} {σ₂} {τ₁} {τ₂} σ₁≈σ₂ τ₁≈τ₂ x =
    trans (cong (apply σ₁) (τ₁≈τ₂ x))
          (σ₁≈σ₂ (apply τ₂ x))

  ⁻¹-cong : {σ τ : Permutation n} → σ ≈ τ → (σ ⁻¹) ≈ (τ ⁻¹)
  ⁻¹-cong {σ} {τ} σ≈τ x =
    let step : apply τ (invₐ σ x) ≡ x
        step = trans (sym (σ≈τ (invₐ σ x))) (inv-r σ x)
    in trans (sym (inv-l τ (invₐ σ x))) (cong (invₐ τ) step)

  ----------------------------------------------------------------------
  -- Bundle as Group.
  ----------------------------------------------------------------------

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

  S-Group : Group 0ℓ 0ℓ
  S-Group = record
    { Carrier = Permutation n
    ; _≈_     = _≈_
    ; _∙_     = _·_
    ; ε       = ε
    ; _⁻¹     = _⁻¹
    ; isGroup = isGroup
    }

  ----------------------------------------------------------------------
  -- Injectivity of apply (from the bijection certificate).
  -- Mirrors σ-injective in Substrate.Cocycles.V4Signature.S4Iso.
  ----------------------------------------------------------------------

  σ-injective : (σ : Permutation n) (x y : Fin n) →
                apply σ x ≡ apply σ y → x ≡ y
  σ-injective σ x y eq =
    trans (sym (inv-l σ x))
          (trans (cong (invₐ σ) eq) (inv-l σ y))

------------------------------------------------------------------------
-- Notes
--
-- 1. This module is the n-parameterised companion to
--    Substrate.Groups.S4. S_4 is NOT literally `Permutation 4` because
--    Substrate.Groups.S4 uses the named-axis type `Axis` for its
--    carrier; the carriers are isomorphic but not definitionally equal.
--    A unification refactor (one parametric module, S_4 as
--    instantiation) is possible but deferred — the existing S_4 work
--    has named-axis idioms in dependent modules (V4-Embedding,
--    SemidirectProduct, S4Iso) that would require porting.
--
-- 2. For CY-2 K-rule cocycle (Substrate.Cocycles.KRule), the variable
--    space V = Fin n, the action of S_n on V is `apply`, and the
--    action on V × V is componentwise. See that module for the
--    full instance.
------------------------------------------------------------------------
