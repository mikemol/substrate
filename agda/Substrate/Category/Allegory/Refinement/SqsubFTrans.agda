------------------------------------------------------------------------
-- Substrate.Category.Allegory.Refinement.SqsubFTrans
--
-- Defines: ⊑ᶠ-trans
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.Category.Allegory.Refinement; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Category.Allegory.Refinement.SqsubFTrans where

open import Substrate.Foundation.Eq.Sym
open import Substrate.Foundation.Eq.Trans
open import Substrate.Foundation.Eq.Cong2
open import Substrate.Category.Allegory.Refinement.Preamble
open import Substrate.Category.Allegory.Refinement.SqsubF



⊑ᶠ-trans : {A : Set} {P Q R : A → Set} → P ⊑ᶠ Q → Q ⊑ᶠ R → P ⊑ᶠ R
⊑ᶠ-trans p q a x = q a (p a x)
