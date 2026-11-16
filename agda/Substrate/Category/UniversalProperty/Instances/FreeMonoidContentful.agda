------------------------------------------------------------------------
-- Substrate.Category.UniversalProperty.Instances.FreeMonoidContentful
--
-- Defines: FreeMonoid-contentful
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.Category.UniversalProperty.Instances; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Category.UniversalProperty.Instances.FreeMonoidContentful where

open import Substrate.Foundation.Nat.Nat
open import Substrate.Foundation.Unit
open import Substrate.Foundation.Empty.Bot
open import Substrate.Foundation.Fin.Fin
open import Substrate.Category.UniversalProperty.Vacuity
open import Substrate.Category.FreeUniversalProperty
open import Substrate.Category.FreeUniversalProperty.FreeMonoid
open import Substrate.Foundation.Eq
open import Substrate.Category.UniversalProperty.Instances.OneNeq0
open import Substrate.Category.UniversalProperty.Instances.FreeMonoidUP
open import Substrate.Foundation.Product



FreeMonoid-contentful : Contentful FreeMonoid-UP
FreeMonoid-contentful = (λ _ → 0) , (λ _ → 1) , λ w → 1≢0 (w tt)
