------------------------------------------------------------------------
-- Substrate.Category.UniversalProperty.Category
--
-- UP7 of the UP-topos arc per [scratch/up_topos_arc_plan.md].
--
-- Packages UPCategory: objects = UPArrows; morphisms = UPTerms
-- (the term-algebra encoding); composition = term concatenation;
-- identity = the empty term.
--
-- Category laws hold STRUCTURALLY at the term level:
--   * id ++ᵤ t  ≡ t    (left identity; refl by [] ++ᵤ y = y)
--   * t ++ᵤ id  ≡ t    (right identity; structural induction on t)
--   * (t ++ᵤ u) ++ᵤ v ≡ t ++ᵤ (u ++ᵤ v)  (associativity; induction)
--
-- All three are mechanical word-algebra theorems (substrate-native
-- per Substrate.Groups.Coxeter.Word). UP4-UP6 already supplied the
-- term-algebra primitives; this slice exhibits the category.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Category.UniversalProperty.Category where

open import Substrate.Foundation.Eq
  using (_≡_; refl; sym; trans; cong)

open import Substrate.Category.UniversalProperty using (UPArrow)
open import Substrate.Category.UniversalProperty.Term
  using (UPTerm; []; _∷_; _++ᵤ_)

------------------------------------------------------------------------
-- 1. Identity and composition (at the term level).
------------------------------------------------------------------------

id-UPTerm : (U : UPArrow) → UPTerm U U
id-UPTerm _ = []

compose-UPTerm :
  {U₁ U₂ U₃ : UPArrow} →
  UPTerm U₂ U₃ → UPTerm U₁ U₂ → UPTerm U₁ U₃
compose-UPTerm g f = f ++ᵤ g

------------------------------------------------------------------------
-- 2. Category laws.
--
-- (a) Left identity: [] ++ᵤ t ≡ t  — definitional, by ++ᵤ's first
--     clause.
-- (b) Right identity: t ++ᵤ [] ≡ t — by induction on t.
-- (c) Associativity: (t ++ᵤ u) ++ᵤ v ≡ t ++ᵤ (u ++ᵤ v) — induction
--     on t.
------------------------------------------------------------------------

++ᵤ-identityˡ :
  {U₁ U₂ : UPArrow} (t : UPTerm U₁ U₂) → ([] ++ᵤ t) ≡ t
++ᵤ-identityˡ _ = refl

++ᵤ-identityʳ :
  {U₁ U₂ : UPArrow} (t : UPTerm U₁ U₂) → (t ++ᵤ []) ≡ t
++ᵤ-identityʳ []       = refl
++ᵤ-identityʳ (x ∷ xs) = cong (x ∷_) (++ᵤ-identityʳ xs)

++ᵤ-assoc :
  {U₁ U₂ U₃ U₄ : UPArrow}
  (t : UPTerm U₁ U₂) (u : UPTerm U₂ U₃) (v : UPTerm U₃ U₄) →
  ((t ++ᵤ u) ++ᵤ v) ≡ (t ++ᵤ (u ++ᵤ v))
++ᵤ-assoc []       u v = refl
++ᵤ-assoc (x ∷ xs) u v = cong (x ∷_) (++ᵤ-assoc xs u v)

------------------------------------------------------------------------
-- 3. The UPCategory record.
--
-- Bundles the term-level data:
--   * Obj = UPArrow
--   * Hom = UPTerm
--   * id, ∘ via term operations
--   * identity + associativity laws
------------------------------------------------------------------------

record UPCategory : Set₂ where
  field
    Obj : Set₁
    Hom : Obj → Obj → Set₁
    id-hom : (X : Obj) → Hom X X
    compose-hom : {X Y Z : Obj} → Hom Y Z → Hom X Y → Hom X Z
    id-leftˡ :
      {X Y : Obj} (f : Hom X Y) →
      compose-hom (id-hom Y) f ≡ f
    id-rightʳ :
      {X Y : Obj} (f : Hom X Y) →
      compose-hom f (id-hom X) ≡ f
    assoc :
      {W X Y Z : Obj}
      (h : Hom Y Z) (g : Hom X Y) (f : Hom W X) →
      compose-hom (compose-hom h g) f
        ≡ compose-hom h (compose-hom g f)

open UPCategory public

------------------------------------------------------------------------
-- 4. The substrate's canonical UPCategory instance.
------------------------------------------------------------------------

UPCategory-canonical : UPCategory
UPCategory-canonical = record
  { Obj         = UPArrow
  ; Hom         = UPTerm
  ; id-hom      = id-UPTerm
  ; compose-hom = compose-UPTerm
  ; id-leftˡ    = λ f → ++ᵤ-identityʳ f
  ; id-rightʳ   = λ f → ++ᵤ-identityˡ f
  ; assoc       = λ h g f → sym (++ᵤ-assoc f g h)
  }

------------------------------------------------------------------------
-- 5. Capstone for UP7.
--
-- UPCategory packaged. Composition is structural word-append;
-- identity is the empty term; associativity is one inductive
-- step. UP8 lands concrete UP-instances; UP9 the terminal +
-- Cat embedding; UP10 the Phase-1 capstone.
------------------------------------------------------------------------
