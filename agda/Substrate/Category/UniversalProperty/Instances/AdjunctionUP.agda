------------------------------------------------------------------------
-- Substrate.Category.UniversalProperty.Instances.AdjunctionUP
--
-- Defines: Adjunction-UP
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.Category.UniversalProperty.Instances; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Category.UniversalProperty.Instances.AdjunctionUP where

open import Substrate.Foundation.Nat.Nat
open import Substrate.Foundation.Empty.Bot
open import Substrate.Foundation.Fin.Fin
open import Substrate.Category.FreeUniversalProperty
open import Substrate.Foundation.Eq



------------------------------------------------------------------------
-- 4. Adjunction — the trivial Free ⊣ Forgetful (free-Set: F = B, η = id).
------------------------------------------------------------------------

Adjunction-UP = FreeUP-UPArrow (λ (b : ℕ) → b) ℕ
