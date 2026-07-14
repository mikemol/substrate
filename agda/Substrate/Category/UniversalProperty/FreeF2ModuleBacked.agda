{-# OPTIONS --safe --without-K #-}

------------------------------------------------------------------------
-- Substrate.Category.UniversalProperty.FreeF2ModuleBacked — finish the free F₂-MODULE
-- deferral (Registry's "PROVED-BUT-NOT-YET-REGISTERED — NOT debt"). ADD 173 scoped
-- this because F2.AsModule proves only the module AXIOMS (no map-OUT). The map-out IS
-- FreeF2Module.ext — the linear extension (sum over the basis), the free-module UP's
-- solve, with extend-unique PROVED (a content-bearing FreeUP for the F₂-module
-- signature). Here it is wrapped as a BackedUP and consed onto the registry.
--
-- The free module on Fin k IS Vector k; ext {M}(Mod) f : Vector k → M is the unique
-- linear map extending f : Fin k → M. Concrete target: M = Vector k itself (vector-
-- F2Mod), f = basis, so ext basis : Vector k → Vector k is the linear extension, and a
-- candidate vector ≠ its extension gives content. Typing certifies the free F₂-module.
------------------------------------------------------------------------

module Substrate.Category.UniversalProperty.FreeF2ModuleBacked where

open import Substrate.Foundation.Eq using (_≡_; refl)
open import Substrate.Foundation.Nat using (ℕ; suc; zero)
open import Substrate.Foundation.Fin using (Fin; zero)
open import Substrate.Foundation.List using (List; []; _∷_)
open import Substrate.Foundation.Negation using (¬_)
open import Substrate.Foundation.Product using (_,_)
open import Substrate.Algebra.F2 using (F₂; 𝟘; 𝟙)
open import Substrate.Algebra.F2.Vector using (Vector; 𝟎ⱽ; basis)
open import Substrate.Category.FreeUniversalProperty.FreeF2Module using (F2Mod; vector-F2Mod; ext)
open import Substrate.Category.UniversalProperty using (UPArrow; Source; Target; Witness)
open import Substrate.Category.UniversalProperty.Vacuity using (Contentful)
open import Substrate.Category.UniversalProperty.Backed using (BackedUP; arrow; backed-non-vacuous)
-- the free module on Fin 1 is Vector 1; target module = Vector 1 itself; basis map.
-- ext (vector-F2Mod 1) basis : Vector 1 → Vector 1 is the linear extension.
linExt : Vector 1 → Vector 1
linExt = ext (vector-F2Mod 1) basis

------------------------------------------------------------------------
-- THE FREE F₂-MODULE UP as a UPArrow: Source = Vector 1 (the free carrier), Target =
-- Vector 1 (the target module), Witness w v = v ≡ linExt w (the linear extension).
------------------------------------------------------------------------
f2mod-UP : UPArrow
f2mod-UP = record
  { Source  = Vector 1
  ; Target  = Vector 1
  ; Witness = λ w v → v ≡ linExt w
  }

f2mod-solve : Source f2mod-UP → Target f2mod-UP
f2mod-solve = linExt

f2mod-solves : (w : Source f2mod-UP) → Witness f2mod-UP w (f2mod-solve w)
f2mod-solves w = refl

-- content: 𝟎ⱽ extends to linExt 𝟎ⱽ = 𝟎ⱽ (ext-zero); candidate basis zero = (𝟙 ∷ …) ≠ 𝟎ⱽ.
-- (the linear extension of the zero vector is zero; a basis vector is not.) Non-vacuous.
f2mod-contentful : Contentful f2mod-UP
f2mod-contentful = 𝟎ⱽ , basis zero , λ ()

f2mod-backed : BackedUP
f2mod-backed = record
  { arrow = f2mod-UP ; solve = f2mod-solve ; solves = f2mod-solves ; content = f2mod-contentful }

f2mod-non-vacuous : ¬ _
f2mod-non-vacuous = backed-non-vacuous f2mod-backed

------------------------------------------------------------------------
-- THE INVARIANT (bottoming out — the free F₂-module deferral finished, the map-out
-- found): F2.AsModule proved the module AXIOMS but had no map-OUT; ADD 173 scoped this
-- honestly. The map-out IS FreeF2Module.ext — the linear extension (sum over the basis),
-- the free-module UP's solve, extend-unique PROVED. f2mod-backed wraps it as a BackedUP,
-- non-vacuous (a basis vector's extension ≠ 𝟎), consed onto the registry — certified by
-- TYPING. The "axioms vs the universal property" either/or dissolves: AsModule gave the
-- STRUCTURE (the module laws), FreeF2Module gives the UNIVERSAL PROPERTY (the unique
-- linear map out); registering needs the latter — the SAME split as the ν's existence
-- (solve) vs its structure. The deferred list: free monoid (172) + Z₂ + units (173) +
-- free F₂-module (174) = 4/5; only the limit/product (⟡register-limit) remains.
------------------------------------------------------------------------
