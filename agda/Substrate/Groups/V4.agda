------------------------------------------------------------------------
-- Substrate.Groups.V4
--
-- The Klein four-group V_4 as a four-element data type with the
-- group structure proved constructively.
--
-- V_4 has four elements:
--   e  -- identity
--   α  -- (DC)(SW) double-transposition
--   β  -- (DS)(CW) double-transposition
--   γ  -- (DW)(CS) double-transposition
--
-- Multiplication table (V_4 is abelian, every element self-inverse):
--
--     ·  | e  α  β  γ
--    ----+------------
--     e  | e  α  β  γ
--     α  | α  e  γ  β
--     β  | β  γ  e  α
--     γ  | γ  β  α  e
--
-- This module proves V_4 forms a Group (in the stdlib sense) so it
-- can be supplied as the `Gauge` field of a CocycleStructure.
--
-- See: catalog/cocycles.md § CY-5 for where V_4 appears in the
-- substrate's gauge structure.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Groups.V4 where

open import Level using (0ℓ)
open import Algebra.Bundles using (Group)
open import Algebra.Definitions
open import Algebra.Structures
open import Relation.Binary.PropositionalEquality
  using (_≡_; refl; sym; trans; cong)
open import Relation.Binary.PropositionalEquality.Properties
  using (isEquivalence)

------------------------------------------------------------------------
-- The carrier
------------------------------------------------------------------------

data V₄ : Set where
  e α β γ : V₄

------------------------------------------------------------------------
-- Group operations
------------------------------------------------------------------------

-- Multiplication. Pattern-matches the Cayley table directly.
_·_ : V₄ → V₄ → V₄
e · y = y
α · e = α
α · α = e
α · β = γ
α · γ = β
β · e = β
β · α = γ
β · β = e
β · γ = α
γ · e = γ
γ · α = β
γ · β = α
γ · γ = e

infixl 7 _·_

-- Identity element.
ε : V₄
ε = e

-- Inverse. Every element is its own inverse in V_4.
inv : V₄ → V₄
inv x = x

------------------------------------------------------------------------
-- Group axioms — proved by exhaustive case analysis (16 cases each).
------------------------------------------------------------------------

·-assoc : Associative _≡_ _·_
·-assoc e _ _ = refl
·-assoc α e _ = refl
·-assoc α α e = refl
·-assoc α α α = refl
·-assoc α α β = refl
·-assoc α α γ = refl
·-assoc α β e = refl
·-assoc α β α = refl
·-assoc α β β = refl
·-assoc α β γ = refl
·-assoc α γ e = refl
·-assoc α γ α = refl
·-assoc α γ β = refl
·-assoc α γ γ = refl
·-assoc β e _ = refl
·-assoc β α e = refl
·-assoc β α α = refl
·-assoc β α β = refl
·-assoc β α γ = refl
·-assoc β β e = refl
·-assoc β β α = refl
·-assoc β β β = refl
·-assoc β β γ = refl
·-assoc β γ e = refl
·-assoc β γ α = refl
·-assoc β γ β = refl
·-assoc β γ γ = refl
·-assoc γ e _ = refl
·-assoc γ α e = refl
·-assoc γ α α = refl
·-assoc γ α β = refl
·-assoc γ α γ = refl
·-assoc γ β e = refl
·-assoc γ β α = refl
·-assoc γ β β = refl
·-assoc γ β γ = refl
·-assoc γ γ e = refl
·-assoc γ γ α = refl
·-assoc γ γ β = refl
·-assoc γ γ γ = refl

ε-left : LeftIdentity _≡_ ε _·_
ε-left _ = refl

ε-right : RightIdentity _≡_ ε _·_
ε-right e = refl
ε-right α = refl
ε-right β = refl
ε-right γ = refl

ε-identity : Identity _≡_ ε _·_
ε-identity = ε-left , ε-right
  where open import Data.Product using (_,_)

inv-left : LeftInverse _≡_ ε inv _·_
inv-left e = refl
inv-left α = refl
inv-left β = refl
inv-left γ = refl

inv-right : RightInverse _≡_ ε inv _·_
inv-right e = refl
inv-right α = refl
inv-right β = refl
inv-right γ = refl

inv-inverse : Inverse _≡_ ε inv _·_
inv-inverse = inv-left , inv-right
  where open import Data.Product using (_,_)

------------------------------------------------------------------------
-- Group congruence: _·_ respects ≡ on both arguments.
------------------------------------------------------------------------

·-cong : Congruent₂ _≡_ _·_
·-cong refl refl = refl

------------------------------------------------------------------------
-- Bundle as a Group (stdlib)
------------------------------------------------------------------------

isMagma : IsMagma _≡_ _·_
isMagma = record
  { isEquivalence = isEquivalence
  ; ∙-cong        = ·-cong
  }

isSemigroup : IsSemigroup _≡_ _·_
isSemigroup = record
  { isMagma = isMagma
  ; assoc   = ·-assoc
  }

isMonoid : IsMonoid _≡_ _·_ ε
isMonoid = record
  { isSemigroup = isSemigroup
  ; identity    = ε-identity
  }

isGroup : IsGroup _≡_ _·_ ε inv
isGroup = record
  { isMonoid = isMonoid
  ; inverse  = inv-inverse
  ; ⁻¹-cong  = λ { refl → refl }
  }

V₄-Group : Group 0ℓ 0ℓ
V₄-Group = record
  { Carrier  = V₄
  ; _≈_      = _≡_
  ; _∙_      = _·_
  ; ε        = ε
  ; _⁻¹      = inv
  ; isGroup  = isGroup
  }

------------------------------------------------------------------------
-- Abelian (bonus — V_4 is commutative).
------------------------------------------------------------------------

·-comm : Commutative _≡_ _·_
·-comm e e = refl
·-comm e α = refl
·-comm e β = refl
·-comm e γ = refl
·-comm α e = refl
·-comm α α = refl
·-comm α β = refl
·-comm α γ = refl
·-comm β e = refl
·-comm β α = refl
·-comm β β = refl
·-comm β γ = refl
·-comm γ e = refl
·-comm γ α = refl
·-comm γ β = refl
·-comm γ γ = refl
