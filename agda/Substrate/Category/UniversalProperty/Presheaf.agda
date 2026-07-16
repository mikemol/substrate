------------------------------------------------------------------------
-- Substrate.Category.UniversalProperty.Presheaf
--
-- UP21 of the UP-topos arc per [scratch/up_topos_arc_plan.md].
--
-- A presheaf on the UP-site is a contravariant functor
--   F : (UPTerm-category)^op → Set
-- Concretely: an assignment of a Set F(U) to each object U : O + an action
-- F(t) : F(U) → F(V) for each UPTerm t : V → U, contravariantly, preserving
-- identity and composition.
--
-- ⟡ta-upterm: the object index is the Set₀ alphabet O (was UPArrowP over
-- arbitrary Sets); the homs are UPTerm O Hom. UPPresheaf STAYS Set₁ (driver C:
-- the `F : O → Set` field), but references the Set₀ term-forms so the telescope
-- UPTerm can retire. (O, Hom) enter via the enclosing section.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Category.UniversalProperty.Presheaf where

open import Substrate.Foundation.Eq using (_≡_)

open import Substrate.Category.UniversalProperty.Term
  using (UPTerm; []; _++ᵤ_)

module _ (O : Set) (Hom : O → O → Set) where

  ------------------------------------------------------------------------
  -- The Presheaf record. F assigns a Set to each object; action is the
  -- contravariant term-action; pres-id / pres-∘ are the functor laws.
  ------------------------------------------------------------------------

  record UPPresheaf : Set₁ where
    field
      F        : O → Set
      action   : {U V : O} → UPTerm O Hom V U → F U → F V
      pres-id  : {U : O} (x : F U) → action ([] {X = U}) x ≡ x
      pres-∘   : {U V X : O} (t : UPTerm O Hom V U) (u : UPTerm O Hom X V) (x : F U) →
                 action (u ++ᵤ t) x ≡ action u (action t x)

  open UPPresheaf public
