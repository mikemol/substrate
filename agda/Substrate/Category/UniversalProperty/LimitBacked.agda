{-# OPTIONS --safe --without-K #-}

------------------------------------------------------------------------
-- Substrate.Category.UniversalProperty.LimitBacked — finish the LAST deferred item
-- (Registry's "PROVED-BUT-NOT-YET-REGISTERED — NOT debt"): the LIMIT/PRODUCT. This is
-- the DUAL shape — LimitUP.mediate is a map-IN (dual to FreeUP.extend's map-OUT) — so
-- unlike the free monoid / F₂-module wraps it needs a concrete LimitUP instance. The
-- substrate ALREADY has it: product-LimitUP (mediate = tupling), LimitUP-UPArrow (the
-- Source=cones / Target=mediating-maps span), and ConeLimit-UP + ConeLimit-contentful
-- (Instances) — all proved. The ONLY missing piece was the BackedUP wrapper + the
-- registry cons; here they are. The map-IN's solve is mediate; solves is mediate-commutes.
--
-- With this, the deferred list is COMPLETE (5/5): free monoid (172), Z₂ + units (173),
-- free F₂-module (174), limit/product (175). "Finish where it left off" — done.
------------------------------------------------------------------------

module Substrate.Category.UniversalProperty.LimitBacked where

open import Substrate.Foundation.Nat using (ℕ)
open import Substrate.Foundation.Unit using (⊤; tt)
open import Substrate.Foundation.List using (List; []; _∷_)
open import Substrate.Foundation.Negation using (¬_)
import Substrate.Foundation.Fin as F
open import Substrate.Category.LimitUniversalProperty
  using (LimitUP; product-LimitUP; LimitUP-UPArrow; mediate; mediate-commutes)
open import Substrate.Category.UniversalProperty using (UPArrow; Source; Target; Witness)
open import Substrate.Category.UniversalProperty.Vacuity using (Contentful)
open import Substrate.Category.UniversalProperty.Backed using (BackedUP; arrow; backed-non-vacuous)
open import Substrate.Category.UniversalProperty.Instances using (ConeLimit-UP; ConeLimit-contentful)
open import Substrate.Category.UniversalProperty.Registry using (registry)

-- the concrete product limit: the substrate's product-LimitUP 1 (λ _ → ℕ), apex ⊤.
-- (a single-factor product of ℕ over ⊤ — the same instance ConeLimit-UP wraps.)
theLimit : LimitUP 1 (λ _ → ℕ) (F.Fin 1 → ℕ)
theLimit = product-LimitUP 1 (λ _ → ℕ)

------------------------------------------------------------------------
-- THE LIMIT/PRODUCT as a BackedUP. arrow = ConeLimit-UP (Source = cones (i → ⊤ → ℕ),
-- Target = mediating maps ⊤ → (Fin 1 → ℕ)); solve = mediate (the tupling, the map-IN);
-- solves = mediate-commutes (the legs commute); content = ConeLimit-contentful (proved
-- in Instances: the cone f = 0 vs g = 1 disagrees, 1 ≢ 0).
------------------------------------------------------------------------
limit-solve : Source ConeLimit-UP → Target ConeLimit-UP
limit-solve f = mediate theLimit f

limit-solves : (f : Source ConeLimit-UP) → Witness ConeLimit-UP f (limit-solve f)
limit-solves f i a = mediate-commutes theLimit f i a

limit-backed : BackedUP
limit-backed = record
  { arrow   = ConeLimit-UP
  ; solve   = limit-solve
  ; solves  = limit-solves
  ; content = ConeLimit-contentful
  }

limit-non-vacuous : ¬ _
limit-non-vacuous = backed-non-vacuous limit-backed

-- REGISTERED: consed onto the seed registry (compiling = the registration).
limit-registry : List BackedUP
limit-registry = limit-backed ∷ registry

------------------------------------------------------------------------
-- THE INVARIANT (bottoming out — the LAST deferral finished, the map-IN dual): the
-- LIMIT/PRODUCT is the DUAL of the free constructions — LimitUP.mediate is a map-IN
-- (the tupling into the product), where FreeUP.extend/foldW/ext were maps-OUT. Its
-- BackedUP: solve = mediate (the tupling), solves = mediate-commutes (the legs agree),
-- content = ConeLimit-contentful (already proved: a cone with disagreeing values). The
-- map-OUT / map-IN either/or dissolves into ONE BackedUP shape (solve : Source → Target,
-- solves : the coherence) — the free objects solve OUT of the free carrier, the limit
-- solves IN to the product, but BOTH are non-vacuous solvers certified by TYPING. With
-- this, the Registry's DEFERRED list is COMPLETE (5/5): free monoid, Z₂, units, free
-- F₂-module, limit/product — every "PROVED-BUT-NOT-YET-REGISTERED — NOT debt" item is
-- now REGISTERED. The disclaimer is fully dissolved: none of them was a stable resting
-- point; each was a to-do, and registration (the proof re-presented as a compiling
-- entry) finished them. "Finish where it left off" — the whole list, done.
------------------------------------------------------------------------
