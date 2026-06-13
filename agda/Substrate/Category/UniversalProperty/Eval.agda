------------------------------------------------------------------------
-- Substrate.Category.UniversalProperty.Eval
--
-- THE TERM ↔ RECORD BRIDGE (user, 2026-06-13: "you want BOTH, because otherwise
-- right now we can't translate between terms and records, and that's a barrier we
-- need to bridge"). The capstone flagged `eval : UPTerm → UPMorphism` as planned
-- (UP5) but it was never built — so the syntactic free-category term and the
-- semantic commuting-square record were unbridged. This builds both directions:
--
--   eval  : UPTerm U₁ U₂ → UPMorphism U₁ U₂   (term → record; realise the stack)
--   reify : UPMorphism U₁ U₂ → UPTerm U₁ U₂   (record → term; a one-generator word)
--
-- and the round-trip `eval ∘ reify ≡ id`. This is the Free⊣Forgetful realisation:
-- UPTerm is free, UPMorphism the structure, eval the unique structure-map, reify
-- the unit. Record-level identity + composition (needed by eval) are built here too
-- (the UP3 "identity + composition" the capstone deferred).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Category.UniversalProperty.Eval where

open import Substrate.Foundation.Eq using (_≡_; refl)

open import Substrate.Category.UniversalProperty using (UPArrow; Source; Target; Witness)
open import Substrate.Category.UniversalProperty.Morphism
  using (UPMorphism; source-map; target-map; coherent)
open import Substrate.Category.UniversalProperty.Term
  using (UPGen; lift; UPTerm; []; _∷_)

------------------------------------------------------------------------
-- Record-level identity and composition of UPMorphisms (UP3).
------------------------------------------------------------------------

id-UPMorphism : (U : UPArrow) → UPMorphism U U
id-UPMorphism U = record
  { source-map = λ s → s
  ; target-map = λ i → i
  ; coherent   = λ s i w → w
  }

-- compose: forward on sources, BACKWARD on targets (the span/arrow-category law);
-- coherent chains the two squares.
compose-UPMorphism : {U₁ U₂ U₃ : UPArrow}
                   → UPMorphism U₂ U₃ → UPMorphism U₁ U₂ → UPMorphism U₁ U₃
compose-UPMorphism g f = record
  { source-map = λ s → source-map g (source-map f s)
  ; target-map = λ i → target-map f (target-map g i)
  ; coherent   = λ s i w → coherent f s (target-map g i) (coherent g (source-map f s) i w)
  }

------------------------------------------------------------------------
-- eval — the term → record bridge. [] ↦ identity; (lift m ∷ t) ↦ compose.
------------------------------------------------------------------------

eval : {U₁ U₂ : UPArrow} → UPTerm U₁ U₂ → UPMorphism U₁ U₂
eval []           = id-UPMorphism _
eval (lift m ∷ t) = compose-UPMorphism (eval t) m

------------------------------------------------------------------------
-- reify — the record → term bridge: a single-generator word.
------------------------------------------------------------------------

reify : {U₁ U₂ : UPArrow} → UPMorphism U₁ U₂ → UPTerm U₁ U₂
reify m = lift m ∷ []

------------------------------------------------------------------------
-- The round-trip: realising a reified morphism returns it (compose-with-identity,
-- by η). So record → term → record = id — the Forgetful side of the bridge.
------------------------------------------------------------------------

eval-reify : {U₁ U₂ : UPArrow} (m : UPMorphism U₁ U₂) → eval (reify m) ≡ m
eval-reify m = refl
