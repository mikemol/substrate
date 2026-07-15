------------------------------------------------------------------------
-- Substrate.Category.UniversalProperty.Instances
--
-- UP8 of the UP-topos arc. Five canonical UPArrow instances exhibiting the
-- substrate's universal-property records AS objects of UPCategory.
--
-- VACUITY-AUDIT REPAIR (2026-06-03): these were ⊤-collapse placeholders
-- ("abstracted via ⊤ ... concrete bridge at UP9"). The real content now
-- exists, so each is wired to its genuine Contentful UPArrow — projected from
-- the real (Set₁) universal property at a concrete target via FreeUP-UPArrow
-- / LimitUP-UPArrow. Each carries its non-vacuity certificate, so the vacuity
-- detector reads them as real (not ⊤). See scratch/up_nonvacuity_policy.md.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Category.UniversalProperty.Instances where

open import Substrate.Foundation.Nat using (ℕ)
open import Substrate.Foundation.Unit using (⊤; tt)
open import Substrate.Foundation.Eq using (_≡_)
open import Substrate.Foundation.Empty using (⊥)
open import Substrate.Foundation.Product using (_,_)
import Substrate.Foundation.Fin as F
open import Substrate.Category.UniversalProperty.Vacuity using (Contentful)
open import Substrate.Category.FreeUniversalProperty using (FreeUP-UPArrow; free-Set)
open import Substrate.Category.FreeUniversalProperty.FreeMonoid using (free-monoid)
open import Substrate.Category.FreeUniversalProperty.FreeF2Module using (free-F2Module)
open import Substrate.Category.LimitUniversalProperty using (LimitUP-UPArrow; product-LimitUP)

private
  1≢0 : (1 ≡ 0) → ⊥
  1≢0 ()

------------------------------------------------------------------------
-- 1. FreeMonoid — Coxeter.Word ⊤ is the free monoid (extend = fold).
------------------------------------------------------------------------

FreeMonoid-UP = FreeUP-UPArrow (free-monoid ⊤) ℕ

FreeMonoid-contentful : Contentful FreeMonoid-UP
FreeMonoid-contentful = (λ _ → 0) , (λ _ → 1) , λ w → 1≢0 (w tt)

------------------------------------------------------------------------
-- 2. FreeModule — Vector k is the free F₂-module on Fin k.
------------------------------------------------------------------------

FreeModule-UP = FreeUP-UPArrow (free-F2Module 1) ℕ

FreeModule-contentful : Contentful FreeModule-UP
FreeModule-contentful = (λ _ → 0) , (λ _ → 1) , λ w → 1≢0 (w F.zero)

------------------------------------------------------------------------
-- 3. Cone / Limit — the product is the limit of a discrete diagram.
------------------------------------------------------------------------

ConeLimit-UP = LimitUP-UPArrow (product-LimitUP 1 (λ _ → ℕ)) ⊤

ConeLimit-contentful : Contentful ConeLimit-UP
ConeLimit-contentful = (λ _ _ → 0) , (λ _ _ → 1) , λ w → 1≢0 (w F.zero tt)

------------------------------------------------------------------------
-- 4. Adjunction — the trivial Free ⊣ Forgetful (free-Set: F = B, η = id).
------------------------------------------------------------------------

Adjunction-UP = FreeUP-UPArrow (free-Set ℕ) ℕ

Adjunction-contentful : Contentful Adjunction-UP
Adjunction-contentful = (λ _ → 0) , (λ _ → 1) , λ w → 1≢0 (w 0)

------------------------------------------------------------------------
-- 5. FreeLinearization — free linearization = the free F₂-module UP
--    (here dim 2; the dedicated FreeLinearization module is the same UP).
------------------------------------------------------------------------

FreeLinearization-UP = FreeUP-UPArrow (free-F2Module 2) ℕ

FreeLinearization-contentful : Contentful FreeLinearization-UP
FreeLinearization-contentful = (λ _ → 0) , (λ _ → 1) , λ w → 1≢0 (w F.zero)
