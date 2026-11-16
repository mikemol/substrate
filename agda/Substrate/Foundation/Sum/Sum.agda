------------------------------------------------------------------------
-- Substrate.Foundation.Sum.Sum
--
-- Defines: _⊎_, inj₁, inj₂
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.Foundation.Sum; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Foundation.Sum.Sum where

open import Substrate.Foundation.Level
open import Substrate.Foundation.Sum.Private

infixr 1 _⊎_


data _⊎_ (A : Set ℓ₁) (B : Set ℓ₂) : Set (ℓ₁ ⊔ ℓ₂) where
  inj₁ : A → A ⊎ B
  inj₂ : B → A ⊎ B
