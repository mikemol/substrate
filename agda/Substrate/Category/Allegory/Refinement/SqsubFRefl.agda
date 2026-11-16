------------------------------------------------------------------------
-- Substrate.Category.Allegory.Refinement.SqsubFRefl
--
-- Defines: ⊑ᶠ-refl
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.Category.Allegory.Refinement; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Category.Allegory.Refinement.SqsubFRefl where

open import Substrate.Foundation.Eq.Sym
open import Substrate.Foundation.Eq.Trans
open import Substrate.Foundation.Eq.Cong2
open import Substrate.Category.Allegory.Refinement.Preamble
open import Substrate.Category.Allegory.Refinement.SqsubF



⊑ᶠ-refl : {A : Set} {P : A → Set} → P ⊑ᶠ P
⊑ᶠ-refl _ p = p
