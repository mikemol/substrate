------------------------------------------------------------------------
-- Substrate.Groups.F2Cubed
--
-- F_2³ — the elementary abelian group of order 8 (three copies of
-- Z/2Z under componentwise XOR). The gauge of CY-4: F_2³ acts on the
-- 8 puncturings of RM(1, 3) by 3-bit XOR on puncture index.
--
-- Carrier: Bool × Bool × Bool.
-- Operation: componentwise xor.
-- Identity: (false, false, false).
-- Inverse: self (every element of F_2³ is its own inverse).
--
-- Self-inverse abelian: F_2³ is the simplest non-cyclic abelian group
-- whose every non-identity element has order 2. V_4 (Klein four-
-- group) is its 2-dimensional analogue; F_2³ is the natural gauge for
-- 3-dimensional binary structures (RM(1, 3) codes, the WHT of length
-- 8, the 8 puncturings of a [8,4,4] code).
--
-- See: catalog/cocycles.md § CY-4 — F_2³ puncturing gauge cocycle.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Groups.F2Cubed where

open import Level using (0ℓ)
open import Algebra.Bundles using (Group)
open import Algebra.Structures
open import Algebra.Definitions using (Congruent₂)
open import Relation.Binary.PropositionalEquality
  using (_≡_; refl; sym; trans; cong; cong₂; isEquivalence)
open import Data.Bool using (Bool; true; false; _xor_)
open import Data.Bool.Properties
  using (xor-assoc; xor-identityˡ; xor-identityʳ; xor-same)
open import Data.Product using (_×_; _,_; proj₁; proj₂)

------------------------------------------------------------------------
-- Carrier.
------------------------------------------------------------------------

F₂³ : Set
F₂³ = Bool × Bool × Bool

------------------------------------------------------------------------
-- Group operations.
------------------------------------------------------------------------

infixl 6 _+_

_+_ : F₂³ → F₂³ → F₂³
(a₁ , a₂ , a₃) + (b₁ , b₂ , b₃) = (a₁ xor b₁ , a₂ xor b₂ , a₃ xor b₃)

ε : F₂³
ε = false , false , false

-- In F_2³ every element is self-inverse, so inversion is the identity
-- function. We name it explicitly for clarity in the Group bundle.
-_ : F₂³ → F₂³
- x = x

------------------------------------------------------------------------
-- Group axioms, lifted componentwise from Data.Bool.Properties.
------------------------------------------------------------------------

+-assoc : (x y z : F₂³) → (x + y) + z ≡ x + (y + z)
+-assoc (a₁ , a₂ , a₃) (b₁ , b₂ , b₃) (c₁ , c₂ , c₃) =
  cong₂ _,_ (xor-assoc a₁ b₁ c₁)
   (cong₂ _,_ (xor-assoc a₂ b₂ c₂)
              (xor-assoc a₃ b₃ c₃))

+-identityˡ : (x : F₂³) → ε + x ≡ x
+-identityˡ (a₁ , a₂ , a₃) =
  cong₂ _,_ (xor-identityˡ a₁)
   (cong₂ _,_ (xor-identityˡ a₂) (xor-identityˡ a₃))

+-identityʳ : (x : F₂³) → x + ε ≡ x
+-identityʳ (a₁ , a₂ , a₃) =
  cong₂ _,_ (xor-identityʳ a₁)
   (cong₂ _,_ (xor-identityʳ a₂) (xor-identityʳ a₃))

-- Self-inverse: x + x ≡ ε, lifted from xor-same.
+-self : (x : F₂³) → x + x ≡ ε
+-self (a₁ , a₂ , a₃) =
  cong₂ _,_ (xor-same a₁)
   (cong₂ _,_ (xor-same a₂) (xor-same a₃))

-- The inverse axioms specialise +-self (since - x = x).
-inverseˡ : (x : F₂³) → (- x) + x ≡ ε
-inverseˡ x = +-self x

-inverseʳ : (x : F₂³) → x + (- x) ≡ ε
-inverseʳ x = +-self x

------------------------------------------------------------------------
-- Congruence of _+_ and -_ with respect to ≡.
------------------------------------------------------------------------

+-cong : Congruent₂ _≡_ _+_
+-cong refl refl = refl

⁻¹-cong : {x y : F₂³} → x ≡ y → - x ≡ - y
⁻¹-cong refl = refl

------------------------------------------------------------------------
-- Bundle as a Group.
------------------------------------------------------------------------

isMagma : IsMagma _≡_ _+_
isMagma = record
  { isEquivalence = isEquivalence
  ; ∙-cong        = +-cong
  }

isSemigroup : IsSemigroup _≡_ _+_
isSemigroup = record
  { isMagma = isMagma
  ; assoc   = +-assoc
  }

isMonoid : IsMonoid _≡_ _+_ ε
isMonoid = record
  { isSemigroup = isSemigroup
  ; identity    = +-identityˡ , +-identityʳ
  }

isGroup : IsGroup _≡_ _+_ ε -_
isGroup = record
  { isMonoid = isMonoid
  ; inverse  = -inverseˡ , -inverseʳ
  ; ⁻¹-cong  = ⁻¹-cong
  }

F₂³-Group : Group 0ℓ 0ℓ
F₂³-Group = record
  { Carrier = F₂³
  ; _≈_     = _≡_
  ; _∙_     = _+_
  ; ε       = ε
  ; _⁻¹     = -_
  ; isGroup = isGroup
  }

------------------------------------------------------------------------
-- Notes
--
-- 1. F_2³ is the simplest non-trivial abelian self-inverse group of
--    rank > 1. V_4 (catalog M41 v16, Substrate.Groups.V4) is its
--    rank-2 analogue. The pattern generalises to F_2^n for all n; in
--    this codebase we keep n=3 specialised since CY-4 specifically
--    instantiates rank 3.
--
-- 2. F_2³ acts on itself by translation (the regular representation),
--    and this action is free transitive — i.e., F_2³ is its own
--    torsor. Substrate.Cocycles.F2CubedPuncturing uses this fact to
--    instantiate IsomorphicCocycleStructure for CY-4.
--
-- 3. Possible follow-on: a Substrate.Groups.F2 module for the
--    underlying F_2 group, then F_2³ as F_2 × F_2 × F_2 via a generic
--    direct-product construction. Deferred — the direct definition
--    here is the smaller artefact for the cocycle's needs.
------------------------------------------------------------------------
