------------------------------------------------------------------------
-- Substrate.Category.UniversalProperty.FreeF2ModuleBackedGraded — ⟡C2g-m-f2mod (graded): the free
-- F₂-module universal property as a Set₀ graded backing.
--
-- Migrates the flat `f2mod-backed : BackedUP` (FreeF2ModuleBacked.agda:60). solve = ext (vector-F2Mod
-- 1) basis (the unique linear extension); `solves` (= refl) vanishes into `Contentfulᴳ`. Constant
-- grade (Spec = Sol = λ _ → Vector 1; the dimension is the native grade if wanted, but const suffices
-- and Vector 1 is already 2-element so non-vacuity is real); content = 𝟎ⱽ extends to 𝟎ⱽ, candidate
-- (basis zero) ≠ it. Class A, CLEAN. Drops the flat `f2mod-registry` cons per ⟡C2g-registry.
--
-- Zero postulates, --safe --without-K.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Category.UniversalProperty.FreeF2ModuleBackedGraded where

open import Substrate.Foundation.Nat using (ℕ)
open import Substrate.Foundation.Fin.Fin
open import Substrate.Foundation.Product using (_,_)
open import Substrate.Algebra.F2.Vector using (Vector; 𝟎ⱽ; basis)
open import Substrate.Category.FreeUniversalProperty.FreeF2Module using (vector-F2Mod; ext)
open import Substrate.Category.UPArrowGraded using (UPArrowᴳ; mkUP)
open import Substrate.Category.UniversalProperty.BackedGraded using (BackedUPᴳ)

-- the free module on Fin 1 is Vector 1; target = Vector 1; basis map. ext … basis is the extension.
linExt : Vector 1 → Vector 1
linExt = ext (vector-F2Mod 1) basis

f2mod-arrowᴳ : UPArrowᴳ (λ _ → Vector 1) (λ _ → Vector 1)
f2mod-arrowᴳ = mkUP linExt

f2mod-backedᴳ : BackedUPᴳ (λ _ → Vector 1) (λ _ → Vector 1)
f2mod-backedᴳ = record
  { arrowᴳ  = f2mod-arrowᴳ
  ; content = 0 , 𝟎ⱽ , basis zero , λ ()
  }
