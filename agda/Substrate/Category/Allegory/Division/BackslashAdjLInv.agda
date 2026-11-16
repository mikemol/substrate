------------------------------------------------------------------------
-- Substrate.Category.Allegory.Division.BackslashAdjLInv
--
-- Defines: ∖-adjˡ⁻
-- The other half of the left-residual adjunction: S ⊆ R∖T → R⨾S ⊆ T.
-- The proof is uncurrying — the inverse of ∖-adjˡ's currying.
--
-- ⟡alg6-restore: recovered from efe21483^ (ALG-6).  One lemma, one
-- elaboration unit; no barrel re-exports these siblings.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Category.Allegory.Division.BackslashAdjLInv where

open import Substrate.Foundation.Product
open import Substrate.Category.Allegory
open import Substrate.Category.Allegory.Division.Backslash


∖-adjˡ⁻ : {A B C : Set} {R : A → B → Set} {S : B → C → Set} {T : A → C → Set}
        → S ⊆ (R ∖ T) → (R ⨾ S) ⊆ T
∖-adjˡ⁻ k a c (b , (r , s)) = k b c s a r
