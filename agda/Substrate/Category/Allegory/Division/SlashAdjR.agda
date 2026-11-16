------------------------------------------------------------------------
-- Substrate.Category.Allegory.Division.SlashAdjR
--
-- Defines: ／-adjʳ
-- One half of the right-residual adjunction: R⨾S ⊆ T → R ⊆ S／T.
--
-- ⟡alg6-restore: recovered from efe21483^ (ALG-6).  One lemma, one
-- elaboration unit; no barrel re-exports these siblings.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Category.Allegory.Division.SlashAdjR where

open import Substrate.Foundation.Product
open import Substrate.Category.Allegory
open import Substrate.Category.Allegory.Division.Slash


／-adjʳ : {A B C : Set} {R : A → B → Set} {S : B → C → Set} {T : A → C → Set}
        → (R ⨾ S) ⊆ T → R ⊆ (S ／ T)
／-adjʳ h a b r c s = h a c (b , (r , s))
