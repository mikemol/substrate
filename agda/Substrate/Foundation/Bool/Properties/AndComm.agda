------------------------------------------------------------------------
-- Substrate.Foundation.Bool.Properties.AndComm
--
-- Defines: ∧-comm
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.Foundation.Bool.Properties; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Foundation.Bool.Properties.AndComm where

open import Substrate.Foundation.Bool.Bool
open import Substrate.Foundation.Bool.And
open import Substrate.Foundation.Eq
-- ∧ / ∨ semilattice laws. Added for the dual-rail evidence connectives
-- (Substrate.Logic.Evidence.Verdict.Connectives), which lift each rail's
-- Bool operations; reusable for any F₂ / Boolean lattice structure.
-- `_∧_` and `_∨_` match on their first argument, so assoc and identityʳ
-- need only split that one (b, c stay free).
------------------------------------------------------------------------

∧-comm : (a b : Bool) → a ∧ b ≡ b ∧ a
∧-comm true  true  = refl
∧-comm true  false = refl
∧-comm false true  = refl
∧-comm false false = refl
