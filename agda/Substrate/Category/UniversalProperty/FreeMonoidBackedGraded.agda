------------------------------------------------------------------------
-- Substrate.Category.UniversalProperty.FreeMonoidBackedGraded — ⟡C2g-m-freemonoid (graded): the
-- free-monoid universal property as a Set₀ graded backing.
--
-- Migrates the flat `freeMonoid-backed : BackedUP` (FreeMonoidBacked.agda:62). solve = foldW (the
-- free extension = the identity on words for the singleton basis map); `solves` (= refl) vanishes
-- into `Contentfulᴳ`. Constant grade (Spec = Sol = λ _ → Word ℕ); content = a word (0 ∷ []) whose
-- candidate [] differs from its fold. Class A, CLEAN. Drops the flat `freeMonoid-registry` cons per
-- ⟡C2g-registry (a homogeneous `List BackedUPᴳ` is impossible; registration = this term typechecks).
--
-- Zero postulates, --safe --without-K.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Category.UniversalProperty.FreeMonoidBackedGraded where

open import Substrate.Foundation.Nat using (ℕ)
open import Substrate.Foundation.Product using (_,_)
open import Substrate.Groups.Coxeter.Word using (Word; []; _∷_)
open import Substrate.Category.FreeUniversalProperty.FreeMonoid using (MonoidOn; word-monoid; foldW)
open import Substrate.Category.UPArrowGraded using (UPArrowᴳ; mkUP)
open import Substrate.Category.UniversalProperty.BackedGraded using (BackedUPᴳ)

-- the concrete target: the free monoid on ℕ (Word ℕ under ++), basis map = singleton.
Mℕ : MonoidOn (Word ℕ)
Mℕ = word-monoid ℕ

singleton : ℕ → Word ℕ
singleton g = g ∷ []

freeMonoid-arrowᴳ : UPArrowᴳ (λ _ → Word ℕ) (λ _ → Word ℕ)
freeMonoid-arrowᴳ = mkUP (λ w → foldW ℕ Mℕ singleton w)

freeMonoid-backedᴳ : BackedUPᴳ (λ _ → Word ℕ) (λ _ → Word ℕ)
freeMonoid-backedᴳ = record
  { arrowᴳ  = freeMonoid-arrowᴳ
  ; content = 0 , (0 ∷ []) , [] , λ ()
  }
