------------------------------------------------------------------------
-- Substrate.Foundation.Bool.Properties.AndDistribROr
--
-- Defines: ∧-distribʳ-∨
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.Foundation.Bool.Properties; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Foundation.Bool.Properties.AndDistribROr where

open import Substrate.Foundation.Eq
open import Substrate.Foundation.Bool.Bool
open import Substrate.Foundation.Bool.And
open import Substrate.Foundation.Bool.Or



∧-distribʳ-∨ : (a b c : Bool) → (a ∨ b) ∧ c ≡ (a ∧ c) ∨ (b ∧ c)
∧-distribʳ-∨ true  true  true  = refl
∧-distribʳ-∨ true  true  false = refl
∧-distribʳ-∨ true  false true  = refl
∧-distribʳ-∨ true  false false = refl
∧-distribʳ-∨ false true  true  = refl
∧-distribʳ-∨ false true  false = refl
∧-distribʳ-∨ false false true  = refl
∧-distribʳ-∨ false false false = refl
