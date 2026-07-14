------------------------------------------------------------------------
-- Substrate.Category.UniversalProperty.Z2BackedGraded — ⟡C2g-m-z2 (graded): the Z₂ presentation UP
-- as a Set₀ graded backing.
--
-- Migrates the flat `z2-backed : BackedUP` (DeferredBacked.agda:58). solve = quotient (parity = the
-- free foldW into (F₂,𝟘,+) sending a ↦ 𝟙); `solves` (= refl) vanishes into `Contentfulᴳ`. Constant
-- grade (Spec = λ _ → Word ⊤, Sol = λ _ → F₂); content = the one-letter word (tt ∷ []) has parity 𝟙,
-- candidate 𝟘 ≠ 𝟙. Class A, CLEAN. Drops the flat `deferred-registry` cons per ⟡C2g-registry.
--
-- Zero postulates, --safe --without-K.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Category.UniversalProperty.Z2BackedGraded where

open import Substrate.Foundation.Unit using (⊤; tt)
open import Substrate.Foundation.Product using (_,_)
open import Substrate.Groups.Coxeter.Word using (Word; []; _∷_)
open import Substrate.Algebra.F2 using (F₂; 𝟘)
open import Substrate.Category.PresentedUniversalProperty.CyclicZ2 using (quotient)
open import Substrate.Category.UPArrowGraded using (UPArrowᴳ; mkUP)
open import Substrate.Category.UniversalProperty.BackedGraded using (BackedUPᴳ)

z2-arrowᴳ : UPArrowᴳ (λ _ → Word ⊤) (λ _ → F₂)
z2-arrowᴳ = mkUP quotient

z2-backedᴳ : BackedUPᴳ (λ _ → Word ⊤) (λ _ → F₂)
z2-backedᴳ = record
  { arrowᴳ  = z2-arrowᴳ
  ; content = 0 , (tt ∷ []) , 𝟘 , λ ()
  }
