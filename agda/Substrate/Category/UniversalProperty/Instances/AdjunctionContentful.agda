------------------------------------------------------------------------
-- Substrate.Category.UniversalProperty.Instances.AdjunctionContentful
--
-- Defines: Adjunction-contentful
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.Category.UniversalProperty.Instances; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Category.UniversalProperty.Instances.AdjunctionContentful where

open import Substrate.Foundation.Nat.Nat
open import Substrate.Foundation.Empty.Bot
open import Substrate.Foundation.Fin.Fin
open import Substrate.Category.UniversalProperty.Vacuity
open import Substrate.Category.FreeUniversalProperty
open import Substrate.Foundation.Eq
open import Substrate.Category.UniversalProperty.Instances.OneNeq0
open import Substrate.Category.UniversalProperty.Instances.AdjunctionUP
open import Substrate.Foundation.Product



Adjunction-contentful : Contentful Adjunction-UP
Adjunction-contentful = (λ _ → 0) , (λ _ → 1) , λ w → 1≢0 (w 0)
