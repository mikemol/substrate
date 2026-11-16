------------------------------------------------------------------------
-- Substrate.ShadowArchitecture.Raven.PhaseTransition.Monotone.SeenMonotoneRaven
--
-- Defines: seen-monotone-raven
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.ShadowArchitecture.Raven.PhaseTransition.Monotone; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.ShadowArchitecture.Raven.PhaseTransition.Monotone.SeenMonotoneRaven where

open import Substrate.Foundation.Bool.Bool
open import Substrate.Foundation.Bool.Or
open import Substrate.Foundation.Fin.Fin
open import Substrate.Foundation.Fin.To
open import Substrate.Foundation.Nat.Nat
-- ⚑ same ban-sweep casualty as the sibling `PriorAelMonotone`: a dropped
-- `renaming (_≤_ to _ℕ≤_)` left `ℕ≤` unbound, and `ℕ≤` has no definer in the tree.
open import Substrate.Foundation.Nat.Le
open import Substrate.Foundation.Vec
open import Substrate.ShadowArchitecture.Raven.Grammar
open import Substrate.ShadowArchitecture.Raven.Poem.Raven
open import Substrate.ShadowArchitecture.Raven.PhaseTransition.IsAñeléTerminal
open import Substrate.ShadowArchitecture.Raven.PhaseTransition.PriorAñelé
open import Substrate.Foundation.Eq
open import Substrate.ShadowArchitecture.Raven.PhaseTransition.Monotone.PriorAelMonotone



seen-monotone-raven :
  ∀ (i j : Fin 18) →
  (toℕ i ≤ toℕ j) →
  prior-añelē? raven i ≡ true →
  prior-añelē? raven j ≡ true
seen-monotone-raven = prior-añelē?-monotone raven
