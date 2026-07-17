------------------------------------------------------------------------
-- Substrate.Linguistic.CategoryOfLanguages
--
-- Y5 of the Yoneda-lift arc per [scratch/yoneda_lift_arc_plan.md].
--
-- The CategoryOfLanguages record: bundles objects (LanguageWitness)
-- + morphisms (LanguageMorphism) + composition (_∘L_) + identity
-- (id-morphism) + category laws (associativity, identity laws up
-- to _≈M_) into a single substrate-internal categorical object.
--
-- Per [[feedback-categorical-name-first]]: this IS the category of
-- languages classified by free construction — the categorical
-- object the peer review framed as "studying objects via how they
-- relate to each other" (the Yoneda perspective).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Linguistic.CategoryOfLanguages where

open import Substrate.Linguistic.Roster using (Lang; witness-of)
open import Substrate.Linguistic.Morphism using (LanguageMorphism)
open import Substrate.Linguistic.IdMorphism using (id-morphism)
open import Substrate.Linguistic.Compose using (_∘L_)
open import Substrate.Linguistic.CategoryLaws
  using (_≈M_; ∘L-identityˡ; ∘L-identityʳ; ∘L-assoc; ≈M-refl)

------------------------------------------------------------------------
-- 1. The CategoryOfLanguages record.
--
-- Bundles the category structure: objects, hom, id, composition,
-- and the three laws (up to ≈M). Object is a PARAMETER now
-- (⟡rc-lang, W5-L3: the mission's enumerable-objects doctrine — the
-- object universe is the Set₀ `Lang` enum, not a held Set₁ family);
-- the record's own level drops to Set₁ (the `Hom : Object → Object →
-- Set` FIELD's type is itself a Set₁ citizen — a parameter never
-- raises the sort, but a Set-valued Π-field still does).
------------------------------------------------------------------------

record CategoryOfLanguages (Object : Set) : Set₁ where
  field
    -- Morphisms
    Hom : Object → Object → Set
    -- Identity
    Id : (L : Object) → Hom L L
    -- Composition
    Compose :
      {L₁ L₂ L₃ : Object} →
      Hom L₂ L₃ → Hom L₁ L₂ → Hom L₁ L₃
    -- Morphism equivalence (extensional)
    _≅_ : {L₁ L₂ : Object} → Hom L₁ L₂ → Hom L₁ L₂ → Set
    -- Category laws
    identityˡ :
      {L₁ L₂ : Object} (f : Hom L₁ L₂) → Compose (Id L₂) f ≅ f
    identityʳ :
      {L₁ L₂ : Object} (f : Hom L₁ L₂) → Compose f (Id L₁) ≅ f
    assoc :
      {L₁ L₂ L₃ L₄ : Object}
      (h : Hom L₃ L₄) (g : Hom L₂ L₃) (f : Hom L₁ L₂) →
      Compose (Compose h g) f ≅ Compose h (Compose g f)

------------------------------------------------------------------------
-- 2. The canonical instance for the substrate's language
-- classification.
--
-- Plugs the Y1-Y4 machinery into the abstract category record, at
-- Object = Lang. Morphisms between Lang objects go through
-- `witness-of`: `Hom l m = LanguageMorphism (witness-of l) (witness-of m)`.
------------------------------------------------------------------------

LanguageCategory : CategoryOfLanguages Lang
LanguageCategory = record
  { Hom       = λ l m → LanguageMorphism (witness-of l) (witness-of m)
  ; Id        = λ l → id-morphism (witness-of l)
  ; Compose   = _∘L_
  ; _≅_       = _≈M_
  ; identityˡ = ∘L-identityˡ
  ; identityʳ = ∘L-identityʳ
  ; assoc     = ∘L-assoc
  }

------------------------------------------------------------------------
-- 3. Capstone for Y5.
--
-- The category of languages is now a substrate-internal object.
-- Y6 demonstrates the class : LanguageWitness → FreeConstructionClass
-- map is functorial; Y7-Y9 build the Yoneda apparatus.
------------------------------------------------------------------------
