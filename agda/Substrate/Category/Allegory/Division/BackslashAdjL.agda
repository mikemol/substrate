------------------------------------------------------------------------
-- Substrate.Category.Allegory.Division.BackslashAdjL
--
-- Defines: ∖-adjˡ
-- One half of the left-residual adjunction: R⨾S ⊆ T → S ⊆ R∖T.
-- The proof is currying.
--
-- ⟡alg6-restore: recovered from efe21483^ (ALG-6).  One lemma, one
-- elaboration unit; no barrel re-exports these siblings.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Category.Allegory.Division.BackslashAdjL where

open import Substrate.Foundation.Product
open import Substrate.Category.Allegory
open import Substrate.Category.Allegory.Division.Backslash


∖-adjˡ : {A B C : Set} {R : A → B → Set} {S : B → C → Set} {T : A → C → Set}
       → (R ⨾ S) ⊆ T → S ⊆ (R ∖ T)
∖-adjˡ h b c s a r = h a c (b , (r , s))
