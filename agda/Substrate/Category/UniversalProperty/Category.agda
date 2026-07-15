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

open import Substrate.Category.UniversalProperty using (UPArrowP)

-- ⟡UPArrow-dissolve C: telescope over UPArrowP.
private variable
  S₁ T₁ S₂ T₂ S₃ T₃ S₄ T₄ : Set
  W₁ : S₁ → T₁ → Set
  W₂ : S₂ → T₂ → Set
  W₃ : S₃ → T₃ → Set
  W₄ : S₄ → T₄ → Set
open import Substrate.Category.UniversalProperty.Term
  using (UPTerm; []; _∷_; _++ᵤ_)

------------------------------------------------------------------------
-- 1. Identity and composition (at the term level).
------------------------------------------------------------------------

id-UPTerm : (U : UPArrowP S₁ T₁ W₁) → UPTerm U U
id-UPTerm _ = []

compose-UPTerm :
  {U₁ : UPArrowP S₁ T₁ W₁} {U₂ : UPArrowP S₂ T₂ W₂} {U₃ : UPArrowP S₃ T₃ W₃} →
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
  {U₁ : UPArrowP S₁ T₁ W₁} {U₂ : UPArrowP S₂ T₂ W₂} (t : UPTerm U₁ U₂) → ([] ++ᵤ t) ≡ t
++ᵤ-identityˡ _ = refl

++ᵤ-identityʳ :
  {U₁ : UPArrowP S₁ T₁ W₁} {U₂ : UPArrowP S₂ T₂ W₂} (t : UPTerm U₁ U₂) → (t ++ᵤ []) ≡ t
++ᵤ-identityʳ []       = refl
++ᵤ-identityʳ (x ∷ xs) = cong (x ∷_) (++ᵤ-identityʳ xs)

++ᵤ-assoc :
  {U₁ : UPArrowP S₁ T₁ W₁} {U₂ : UPArrowP S₂ T₂ W₂} {U₃ : UPArrowP S₃ T₃ W₃} {U₄ : UPArrowP S₄ T₄ W₄}
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

-- ⟡set1-paydown: parameterize the object collection Obj : Set₁ and the hom-family
-- Hom : Obj → Obj → Set₁ out of the record (substrate stance: carriers/families are
-- params, never fields). They were the only Set₂ source, so the record drops from
-- Set₂ to Set₁; consumers write `UPCategory Obj Hom`.
record UPCategory (Obj : Set₁) (Hom : Obj → Obj → Set₁) : Set₁ where
  field
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

-- ⟡UPArrow-dissolve C: UPCategory-canonical RETIRED — the UPArrowP telescope has
-- no single Set₀/Set₁ object TYPE to pass as `Obj`, and the mission rejects a
-- Σ-bundle object type. The generic UPCategory record (parameterized over any
-- Obj/Hom) stays; the term-level id-UPTerm/compose-UPTerm/++ᵤ-laws above ARE the
-- category structure, now telescope-indexed. (⟡UPGen-ℕ-index would supply a Set₀
-- Obj to re-instantiate this, deferred.)

------------------------------------------------------------------------
-- 5. Capstone for UP7.
--
-- UPCategory packaged. Composition is structural word-append;
-- identity is the empty term; associativity is one inductive
-- step. UP8 lands concrete UP-instances; UP9 the terminal +
-- Cat embedding; UP10 the Phase-1 capstone.
------------------------------------------------------------------------
