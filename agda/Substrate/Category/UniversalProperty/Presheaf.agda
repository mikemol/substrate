------------------------------------------------------------------------
-- Substrate.Category.UniversalProperty.Presheaf
--
-- UP21 of the UP-topos arc per [scratch/up_topos_arc_plan.md].
--
-- A presheaf on UPCategory is a contravariant functor
--   F : UPCategory^op → Set
-- Concretely (at the term-algebra level): an assignment of a Set
-- F(U) to each UPArrow U + an action F(t) : F(U) → F(V) for each
-- UPTerm t : V → U, contravariantly, preserving identity and
-- composition.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Category.UniversalProperty.Presheaf where

open import Substrate.Foundation.Eq using (_≡_)

open import Substrate.Category.UniversalProperty using (UPArrow)
open import Substrate.Category.UniversalProperty.Term
  using (UPTerm; []; _++ᵤ_)

------------------------------------------------------------------------
-- 1. The Presheaf record.
------------------------------------------------------------------------

-- ⟡set1-paydown: NEEDS-DEMATERIALIZE (report, not forced).  The Set₂ source is
-- `F : UPArrow → Set` — the presheaf's object-assignment, a heterogeneous
-- Set-family over the (infinite) index UPArrow, not a flat carrier.  It cannot
-- be a plain module parameter because the whole downstream sheaf arc treats
-- `UPPresheaf` as the type of ALL presheaves and quantifies over it: the
-- PSh→PSh functors (InternalHomType, PowersetType, SheafifyType), constant-
-- Presheaf : Set → UPPresheaf, the Sheaf.presheaf field, MatchingFamily/Sheaf-
-- Pullback (which import the `F`/`action` projections by name).  Parameterizing
-- F out would replace every bare `UPPresheaf` with `Σ (UPArrow → Set) UPPresheaf`
-- — re-materializing the existential across ~12 modules.  Eliminating the Set₂
-- here needs dematerializing the object-assignment (element-category / discrete-
-- fibration presentation), a design change out of scope for the paydown.
record UPPresheaf : Set₂ where
  field
    F        : UPArrow → Set
    action   : {U V : UPArrow} →
               UPTerm V U → F U → F V
    pres-id  : {U : UPArrow} (x : F U) → action {U} {U} [] x ≡ x
    pres-∘   : {U V W : UPArrow}
               (t : UPTerm V U) (u : UPTerm W V) (x : F U) →
               action (u ++ᵤ t) x ≡ action u (action t x)

open UPPresheaf public

------------------------------------------------------------------------
-- 2. Capstone for UP21.
--
-- Presheaf record lands. UP22 supplies the Yoneda embedding
-- よ : UPCategory → PSh(UPCategory); UP23 the sheaf condition.
------------------------------------------------------------------------
