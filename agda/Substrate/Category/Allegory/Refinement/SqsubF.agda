------------------------------------------------------------------------
-- Substrate.Category.Allegory.Refinement.SqsubF
--
-- Defines: _⊑ᶠ_
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.Category.Allegory.Refinement; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Category.Allegory.Refinement.SqsubF where

open import Substrate.Foundation.Eq.Sym
open import Substrate.Foundation.Eq.Trans
open import Substrate.Foundation.Eq.Cong2
open import Substrate.Category.Allegory.Refinement.Preamble

infix 4 _⊑ᶠ_

_⊑ᶠ_ : {A : Set} → (A → Set) → (A → Set) → Set
_⊑ᶠ_ {A} P Q = (a : A) → P a → Q a
