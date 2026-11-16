------------------------------------------------------------------------
-- Substrate.Category.Allegory.Division.SlashAdjRInv
--
-- Defines: ／-adjʳ⁻
-- The other half of the right-residual adjunction: R ⊆ S／T → R⨾S ⊆ T.
--
-- ⟡alg6-restore: recovered from efe21483^ (ALG-6).  One lemma, one
-- elaboration unit; no barrel re-exports these siblings.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Category.Allegory.Division.SlashAdjRInv where

open import Substrate.Foundation.Product
open import Substrate.Category.Allegory
open import Substrate.Category.Allegory.Division.Slash


／-adjʳ⁻ : {A B C : Set} {R : A → B → Set} {S : B → C → Set} {T : A → C → Set}
         → R ⊆ (S ／ T) → (R ⨾ S) ⊆ T
／-adjʳ⁻ k a c (b , (r , s)) = k a b r c s
