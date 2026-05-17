------------------------------------------------------------------------
-- Substrate.Groups.V4
--
-- The Klein four-group V₄ as a 4-element data type, with all
-- algebraic structure (operation, identity, inverse, axioms, stdlib
-- Group bundle) sourced from Substrate.Groups.V4-Coxeter via a
-- bijection.
--
-- V₄ has four elements:
--   e  -- identity
--   α  -- (DC)(SW) double-transposition
--   β  -- (DS)(CW) double-transposition
--   γ  -- (DW)(CS) double-transposition
--
-- Multiplication table:
--
--     ·  | e  α  β  γ
--    ----+------------
--     e  | e  α  β  γ
--     α  | α  e  γ  β
--     β  | β  γ  e  α
--     γ  | γ  β  α  e
--
-- Architecture (per [[feedback-composable-primitives-over-flat-
-- enumeration]] and [[feedback-v4-typeclass-architecture]]): this
-- file keeps the 4-constructor data type as the user-facing V₄
-- (preserving every downstream pattern match) while delegating ALL
-- algebra to V4-Coxeter. This retires Substrate.Groups.V4-Generic
-- (the F₂²-bijection backend) by replacing it with the Coxeter
-- backend; the V₄ vocabulary is unchanged downstream.
--
-- For interop, V₄→F₂² / F₂²→V₄ are also provided (used by V4-
-- Embedding's Axis-is-V₄; will be retired by Shadow D).
--
-- See: catalog/cocycles.md § CY-5 for V₄'s gauge role;
--      Substrate.Groups.V4-Coxeter for the algebra backend;
--      Substrate.Groups.V4-as-Z2xZ2 for the Z/2 × Z/2 decomposition.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Groups.V4 where

open import Data.Bool using (Bool; true; false; _xor_)
open import Data.Product using (_×_; _,_; proj₁; proj₂)
open import Level using (0ℓ)
open import Algebra.Bundles using (Group)
open import Algebra.Definitions
open import Algebra.Structures
open import Relation.Binary.PropositionalEquality
  using (_≡_; refl; sym; trans; cong; cong₂; _≢_)
open import Relation.Binary.PropositionalEquality.Properties
  using (isEquivalence)

import Substrate.Groups.V4-Coxeter as C
open import Substrate.Groups.Coxeter.Word using ([]; _∷_)

------------------------------------------------------------------------
-- 1. The carrier.
------------------------------------------------------------------------

data V₄ : Set where
  e α β γ : V₄

------------------------------------------------------------------------
-- 2. Bijection V₄ ↔ V4-Coxeter canonical Words.
--
-- to-c maps each constructor to its canonical word form.
-- from-c-canonical dispatches on Canonical proofs.
-- from-c first normalizes then dispatches; round-trips established.
------------------------------------------------------------------------

to-c : V₄ → C.Word C.Gen
to-c e = []
to-c α = C.A ∷ []
to-c β = C.B ∷ []
to-c γ = C.A ∷ C.B ∷ []

to-c-canonical : (x : V₄) → C.Canonical (to-c x)
to-c-canonical e = C.c-ε
to-c-canonical α = C.c-A
to-c-canonical β = C.c-B
to-c-canonical γ = C.c-AB

from-c-canonical : {w : C.Word C.Gen} → C.Canonical w → V₄
from-c-canonical C.c-ε  = e
from-c-canonical C.c-A  = α
from-c-canonical C.c-B  = β
from-c-canonical C.c-AB = γ

from-c : C.Word C.Gen → V₄
from-c w = from-c-canonical (C.normalize-canonical w)

-- Round-trips.
from-to : (x : V₄) → from-c (to-c x) ≡ x
from-to e = refl
from-to α = refl
from-to β = refl
from-to γ = refl

to-from-canonical :
  {w : C.Word C.Gen} (c : C.Canonical w) → to-c (from-c-canonical c) ≡ w
to-from-canonical C.c-ε  = refl
to-from-canonical C.c-A  = refl
to-from-canonical C.c-B  = refl
to-from-canonical C.c-AB = refl

------------------------------------------------------------------------
-- 3. Group operations, all routed through V4-Coxeter.
------------------------------------------------------------------------

infixl 7 _·_

_·_ : V₄ → V₄ → V₄
x · y = from-c (to-c x C.· to-c y)

ε : V₄
ε = e

inv : V₄ → V₄
inv x = x  -- V₄ is exponent-2; every element is self-inverse

------------------------------------------------------------------------
-- 4. Bridging lemma: from-c of any Coxeter word.
--
-- For w with canonical proof c, from-c w ≡ from-c-canonical c when
-- the Canonical proof matches normalize-canonical w. Used by the
-- axiom proofs to chain through specific canonical forms.
------------------------------------------------------------------------

-- The key transport: V₄ equality after the bijection IS Word equality
-- on the Coxeter side (under to-c). Used as a bridge through the
-- bijection round-trips.
private
  cong-from-c-canonical :
    {w₁ w₂ : C.Word C.Gen}
    (c₁ : C.Canonical w₁) (c₂ : C.Canonical w₂) →
    w₁ ≡ w₂ → from-c-canonical c₁ ≡ from-c-canonical c₂
  cong-from-c-canonical C.c-ε  C.c-ε  refl = refl
  cong-from-c-canonical C.c-A  C.c-A  refl = refl
  cong-from-c-canonical C.c-B  C.c-B  refl = refl
  cong-from-c-canonical C.c-AB C.c-AB refl = refl

------------------------------------------------------------------------
-- 5. Group axioms via the bijection.
--
-- Each axiom unfolds the V₄ operation to its Coxeter image, applies
-- the corresponding Coxeter lemma, and round-trips back to V₄.
------------------------------------------------------------------------

·-cong : Congruent₂ _≡_ _·_
·-cong refl refl = refl

-- ε-left and ε-right: 4 cases each (direct Cayley refl, since each
-- input pattern lets Agda reduce x · y to the canonical word
-- definitionally).
ε-left : LeftIdentity _≡_ ε _·_
ε-left e = refl
ε-left α = refl
ε-left β = refl
ε-left γ = refl

ε-right : RightIdentity _≡_ ε _·_
ε-right e = refl
ε-right α = refl
ε-right β = refl
ε-right γ = refl

ε-identity : Identity _≡_ ε _·_
ε-identity = ε-left , ε-right

-- inv-left/right: V₄ self-inverse — every x satisfies x · x ≡ ε.
-- 4 refl cases via Coxeter's definitional reductions.
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

-- ·-assoc: 64 cases via direct Cayley computation.
-- Each (x, y, z) triple makes (x · y) · z and x · (y · z) reduce to
-- the same canonical word definitionally.
·-assoc : Associative _≡_ _·_
·-assoc e e e = refl
·-assoc e e α = refl
·-assoc e e β = refl
·-assoc e e γ = refl
·-assoc e α e = refl
·-assoc e α α = refl
·-assoc e α β = refl
·-assoc e α γ = refl
·-assoc e β e = refl
·-assoc e β α = refl
·-assoc e β β = refl
·-assoc e β γ = refl
·-assoc e γ e = refl
·-assoc e γ α = refl
·-assoc e γ β = refl
·-assoc e γ γ = refl
·-assoc α e e = refl
·-assoc α e α = refl
·-assoc α e β = refl
·-assoc α e γ = refl
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
·-assoc β e e = refl
·-assoc β e α = refl
·-assoc β e β = refl
·-assoc β e γ = refl
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
·-assoc γ e e = refl
·-assoc γ e α = refl
·-assoc γ e β = refl
·-assoc γ e γ = refl
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

-- ·-comm: 16 cases (4 × 4).
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

-- ·-right-cancel-ε: a · b ≡ b ⟹ a ≡ ε.
-- "Right-cancelling by b yields the identity." Derived group identity.
-- 16 refl cases; absurd patterns where the equation is contradicted.
·-right-cancel-ε : (a b : V₄) → a · b ≡ b → a ≡ ε
·-right-cancel-ε e e _    = refl
·-right-cancel-ε e α _    = refl
·-right-cancel-ε e β _    = refl
·-right-cancel-ε e γ _    = refl
·-right-cancel-ε α e ()
·-right-cancel-ε α α ()
·-right-cancel-ε α β ()
·-right-cancel-ε α γ ()
·-right-cancel-ε β e ()
·-right-cancel-ε β α ()
·-right-cancel-ε β β ()
·-right-cancel-ε β γ ()
·-right-cancel-ε γ e ()
·-right-cancel-ε γ α ()
·-right-cancel-ε γ β ()
·-right-cancel-ε γ γ ()

------------------------------------------------------------------------
-- 6. Stdlib Group bundle.
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
-- 7. Sanity check: canonical 4-product.
------------------------------------------------------------------------

V₄-canonical-4-product : e · α · β · γ ≡ e
V₄-canonical-4-product = refl

------------------------------------------------------------------------
-- 8. V₄-4-product (delegated to V4-Coxeter).
--
-- 4 pairwise-distinct V₄ elements multiply to ε. The 124-pattern
-- enumeration lives in V4-Coxeter (operates on canonical Words);
-- this V₄-level wrapper just bridges ctor inequalities to Word
-- inequalities and lifts the ε ≈ ε result back through the
-- bijection. ~25 lines vs the 124-pattern enumeration it replaces.
--
-- Consumed by Substrate.Groups.V4-Normality (`case-any-no-fix`).
------------------------------------------------------------------------

private
  -- to-c is injective: distinct V₄ ctors map to distinct canonical
  -- Words. 4 refl + 12 absurd cases.
  to-c-injective : (x y : V₄) → to-c x ≡ to-c y → x ≡ y
  to-c-injective e e _  = refl
  to-c-injective α α _  = refl
  to-c-injective β β _  = refl
  to-c-injective γ γ _  = refl
  to-c-injective e α ()
  to-c-injective e β ()
  to-c-injective e γ ()
  to-c-injective α e ()
  to-c-injective α β ()
  to-c-injective α γ ()
  to-c-injective β e ()
  to-c-injective β α ()
  to-c-injective β γ ()
  to-c-injective γ e ()
  to-c-injective γ α ()
  to-c-injective γ β ()

  -- Lift V₄ inequality to canonical-Word inequality via to-c.
  -- normalize on canonical Words is identity (canonical-is-fixed),
  -- so normalize-equality on canonical Words IS Word-equality, which
  -- to-c-injective converts back to V₄-equality.
  ≢→≉ : {x y : V₄} → x ≢ y → to-c x C.≉ to-c y
  ≢→≉ {x} {y} ineq normalize-eq =
    ineq (to-c-injective x y
            (trans (sym (C.canonical-is-fixed-V4 (to-c-canonical x)))
                   (trans normalize-eq
                          (C.canonical-is-fixed-V4 (to-c-canonical y)))))

  -- Bridge: to-c (a · b) ≡ to-c a C.· to-c b.
  -- LHS = to-c (from-c (to-c a C.· to-c b)) = normalize (to-c a C.· to-c b)
  --     = normalize (normalize (to-c a ++ to-c b))
  --     = normalize (to-c a ++ to-c b)  [normalize-idem]
  --     = to-c a C.· to-c b              [by def of C._·_]
  to-c-· : (a b : V₄) → to-c (a · b) ≡ to-c a C.· to-c b
  to-c-· a b =
    trans (to-from-canonical
            (C.normalize-canonical (to-c a C.· to-c b)))
          (C.normalize-idem (to-c a C.++ to-c b))

V₄-4-product :
  (a b c d : V₄) →
  a ≢ b → a ≢ c → a ≢ d → b ≢ c → b ≢ d → c ≢ d →
  (a · b) · (c · d) ≡ ε
V₄-4-product a b c d a≢b a≢c a≢d b≢c b≢d c≢d =
  -- Strategy: apply V4-Coxeter.V₄-4-product on (to-c a, to-c b,
  -- to-c c, to-c d) for the Coxeter side. The result lives at
  -- the Word level; lift it to V₄ via to-c-injective + a normalize
  -- alignment using to-c-· at each application of V₄'s _·_.
  to-c-injective ((a · b) · (c · d)) e bridge
  where
    coxeter-result :
      ((to-c a C.· to-c b) C.· (to-c c C.· to-c d)) C.≈ []
    coxeter-result =
      C.V₄-4-product (to-c a) (to-c b) (to-c c) (to-c d)
        (≢→≉ a≢b) (≢→≉ a≢c) (≢→≉ a≢d)
        (≢→≉ b≢c) (≢→≉ b≢d) (≢→≉ c≢d)

    -- Bridge: to-c ((a · b) · (c · d)) ≡ to-c e = [].
    -- Decompose:
    --   to-c ((a · b) · (c · d))
    --     ≡ C.normalize (to-c (a · b) C.++ to-c (c · d))     [to-c-· at outer]
    --     ≡ C.normalize (C.normalize (to-c a C.++ to-c b) C.++
    --                    C.normalize (to-c c C.++ to-c d))  [to-c-· × 2 + cong]
    -- coxeter-result has the same final form (after C.· unfolding +
    -- canonical-is-fixed), giving ≡ [].
    bridge : to-c ((a · b) · (c · d)) ≡ []
    bridge =
      trans (to-c-· (a · b) (c · d))
      (trans (cong (λ x → C.normalize (x C.++ to-c (c · d)))
                   (to-c-· a b))
      (trans (cong (λ x → C.normalize ((to-c a C.· to-c b) C.++ x))
                   (to-c-· c d))
      (trans (sym (C.normalize-idem
                    ((to-c a C.· to-c b) C.++ (to-c c C.· to-c d))))
             coxeter-result)))
