------------------------------------------------------------------------
-- Substrate.Category.UniversalProperty.Instances.ConeLimitContentful
--
-- Defines: ConeLimit-contentful
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.Category.UniversalProperty.Instances; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Category.UniversalProperty.Instances.ConeLimitContentful where

open import Substrate.Foundation.Nat.Nat
open import Substrate.Foundation.Unit
open import Substrate.Foundation.Empty.Bot
open import Substrate.Foundation.Fin.Fin
open import Substrate.Category.UniversalProperty.Vacuity
open import Substrate.Category.LimitUniversalProperty
open import Substrate.Foundation.Eq
open import Substrate.Category.UniversalProperty.Instances.OneNeq0
open import Substrate.Category.UniversalProperty.Instances.ConeLimitUP
open import Substrate.Foundation.Product



ConeLimit-contentful : Contentful ConeLimit-UP
ConeLimit-contentful = (λ _ _ → 0) , (λ _ _ → 1) , λ w → 1≢0 (w fzero tt)
