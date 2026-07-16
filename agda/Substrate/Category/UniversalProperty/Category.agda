------------------------------------------------------------------------
-- Substrate.Category.UniversalProperty.Category
--
-- UP7 of the UP-topos arc — the UPCategory record + the canonical instance,
-- now fully at Set₀ (⟡ta-upterm-retire: the telescope laws over UPArrowP are
-- gone; these ARE the former O-forms, promoted).
--
-- Objects = a Set₀ alphabet O; morphisms = UPTerm O Hom (the free-category
-- term-algebra); id = []; composition = _++ᵤ_ (append). The category laws
-- hold STRUCTURALLY (mechanical cons-list induction). UPCategory itself is
-- LEVEL-POLYMORPHIC so it accepts both the Set₀ canonical instance and the
-- Set₁ presheaf-object families.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Category.UniversalProperty.Category where

open import Substrate.Foundation.Eq using (_≡_; refl; sym; cong)
open import Substrate.Foundation.Level using (Level; _⊔_)

open import Substrate.Category.UniversalProperty.Term
  using (UPTerm; []; _∷_; _++ᵤ_)

------------------------------------------------------------------------
-- 1. Identity and composition (at the term level).
------------------------------------------------------------------------

id-UPTerm : {O : Set} {Hom : O → O → Set} (X : O) → UPTerm O Hom X X
id-UPTerm _ = []

compose-UPTerm : {O : Set} {Hom : O → O → Set} {X Y Z : O}
               → UPTerm O Hom Y Z → UPTerm O Hom X Y → UPTerm O Hom X Z
compose-UPTerm g f = f ++ᵤ g

------------------------------------------------------------------------
-- 2. Category laws (structural cons-list induction).
------------------------------------------------------------------------

++ᵤ-identityˡ : {O : Set} {Hom : O → O → Set} {X Y : O} (t : UPTerm O Hom X Y) → ([] ++ᵤ t) ≡ t
++ᵤ-identityˡ _ = refl

++ᵤ-identityʳ : {O : Set} {Hom : O → O → Set} {X Y : O} (t : UPTerm O Hom X Y) → (t ++ᵤ []) ≡ t
++ᵤ-identityʳ []       = refl
++ᵤ-identityʳ (x ∷ xs) = cong (x ∷_) (++ᵤ-identityʳ xs)

++ᵤ-assoc : {O : Set} {Hom : O → O → Set} {X Y Z W : O}
          (t : UPTerm O Hom X Y) (u : UPTerm O Hom Y Z) (v : UPTerm O Hom Z W) →
          ((t ++ᵤ u) ++ᵤ v) ≡ (t ++ᵤ (u ++ᵤ v))
++ᵤ-assoc []       u v = refl
++ᵤ-assoc (x ∷ xs) u v = cong (x ∷_) (++ᵤ-assoc xs u v)

------------------------------------------------------------------------
-- 3. The UPCategory record (LEVEL-POLYMORPHIC).
------------------------------------------------------------------------

record UPCategory {ℓ₀ ℓ₁ : Level} (Obj : Set ℓ₀) (Hom : Obj → Obj → Set ℓ₁) : Set (ℓ₀ ⊔ ℓ₁) where
  field
    id-hom : (X : Obj) → Hom X X
    compose-hom : {X Y Z : Obj} → Hom Y Z → Hom X Y → Hom X Z
    id-leftˡ : {X Y : Obj} (f : Hom X Y) → compose-hom (id-hom Y) f ≡ f
    id-rightʳ : {X Y : Obj} (f : Hom X Y) → compose-hom f (id-hom X) ≡ f
    assoc :
      {W X Y Z : Obj} (h : Hom Y Z) (g : Hom X Y) (f : Hom W X) →
      compose-hom (compose-hom h g) f ≡ compose-hom h (compose-hom g f)

open UPCategory public

------------------------------------------------------------------------
-- 4. The canonical UPCategory instance: objects = O, homs = UPTerm O Hom.
-- The ˡ/ʳ swap is real (compose g f = f ++ᵤ g).
------------------------------------------------------------------------

UPCategory-canonical : (O : Set) (Hom : O → O → Set) → UPCategory O (UPTerm O Hom)
UPCategory-canonical O Hom = record
  { id-hom      = id-UPTerm
  ; compose-hom = compose-UPTerm
  ; id-leftˡ    = λ f → ++ᵤ-identityʳ f
  ; id-rightʳ   = λ f → ++ᵤ-identityˡ f
  ; assoc       = λ h g f → sym (++ᵤ-assoc f g h)
  }
