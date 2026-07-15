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
open import Substrate.Foundation.Level using (Level; _⊔_)

open import Substrate.Category.UniversalProperty using (UPArrowP)

-- ⟡UPArrow-dissolve C: telescope over UPArrowP.
private variable
  S₁ T₁ S₂ T₂ S₃ T₃ S₄ T₄ : Set
  W₁ : S₁ → T₁ → Set
  W₂ : S₂ → T₂ → Set
  W₃ : S₃ → T₃ → Set
  W₄ : S₄ → T₄ → Set
open import Substrate.Category.UniversalProperty.Term
  using (UPTerm; []; _∷_; _++ᵤ_; UPTermO; []O; _∷O_; _++ᵤO_)

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

-- ⟡set1-paydown: parameterize the object collection Obj and the hom-family
-- Hom : Obj → Obj → … out of the record (substrate stance: carriers/families are
-- params, never fields). ⟡ta-upterm FLAG (ii): the record is LEVEL-POLYMORPHIC —
-- Obj : Set ℓ₀, Hom : Obj → Obj → Set ℓ₁, record : Set (ℓ₀ ⊔ ℓ₁) — so it accepts
-- BOTH a Set₀ object alphabet O (the canonical UPTermO instance below, ℓ₀ = ℓ₁ = 0)
-- AND the old Set₁ families (ℓ₀ = ℓ₁ = 1). Consumers write `UPCategory Obj Hom`.
record UPCategory {ℓ₀ ℓ₁ : Level} (Obj : Set ℓ₀) (Hom : Obj → Obj → Set ℓ₁) : Set (ℓ₀ ⊔ ℓ₁) where
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

-- ⟡ta-upterm: UPCategory-canonical REINSTATED over the O-parameterized Set₀ forms
-- (Term.agda's UPTermO). The term-level id/compose/laws collapse to the object index
-- {X : O}; UPCategory is now level-polymorphic (FLAG ii), so its Obj = O : Set₀ fits.
-- These O-forms COEXIST with the telescope forms above until the ~12 sheaf consumers
-- migrate to the module Site (O)(Hom) telescope, then the telescope forms are deleted
-- and the O-forms renamed. (Retires the ⟡UPGen-ℕ-index deferral: no ℕ-index needed —
-- O IS the Set₀ object alphabet.)

id-UPTermO : {O : Set} {Hom : O → O → Set} (X : O) → UPTermO O Hom X X
id-UPTermO _ = []O

compose-UPTermO :
  {O : Set} {Hom : O → O → Set} {X Y Z : O} →
  UPTermO O Hom Y Z → UPTermO O Hom X Y → UPTermO O Hom X Z
compose-UPTermO g f = f ++ᵤO g

++ᵤO-identityˡ :
  {O : Set} {Hom : O → O → Set} {X Y : O} (t : UPTermO O Hom X Y) → ([]O ++ᵤO t) ≡ t
++ᵤO-identityˡ _ = refl

++ᵤO-identityʳ :
  {O : Set} {Hom : O → O → Set} {X Y : O} (t : UPTermO O Hom X Y) → (t ++ᵤO []O) ≡ t
++ᵤO-identityʳ []O       = refl
++ᵤO-identityʳ (x ∷O xs) = cong (x ∷O_) (++ᵤO-identityʳ xs)

++ᵤO-assoc :
  {O : Set} {Hom : O → O → Set} {X Y Z W : O}
  (t : UPTermO O Hom X Y) (u : UPTermO O Hom Y Z) (v : UPTermO O Hom Z W) →
  ((t ++ᵤO u) ++ᵤO v) ≡ (t ++ᵤO (u ++ᵤO v))
++ᵤO-assoc []O       u v = refl
++ᵤO-assoc (x ∷O xs) u v = cong (x ∷O_) (++ᵤO-assoc xs u v)

-- The canonical instance: objects = O, homs = UPTermO O Hom, identity = []O,
-- composition = ++ᵤO. The ˡ/ʳ swap is real (compose g f = f ++ᵤO g).
UPCategory-canonical : (O : Set) (Hom : O → O → Set) → UPCategory O (UPTermO O Hom)
UPCategory-canonical O Hom = record
  { id-hom      = id-UPTermO
  ; compose-hom = compose-UPTermO
  ; id-leftˡ    = λ f → ++ᵤO-identityʳ f
  ; id-rightʳ   = λ f → ++ᵤO-identityˡ f
  ; assoc       = λ h g f → sym (++ᵤO-assoc f g h)
  }

------------------------------------------------------------------------
-- 5. Capstone for UP7.
--
-- UPCategory packaged. Composition is structural word-append;
-- identity is the empty term; associativity is one inductive
-- step. UP8 lands concrete UP-instances; UP9 the terminal +
-- Cat embedding; UP10 the Phase-1 capstone.
------------------------------------------------------------------------
