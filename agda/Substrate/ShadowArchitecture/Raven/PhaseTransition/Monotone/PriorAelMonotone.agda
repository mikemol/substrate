------------------------------------------------------------------------
-- Substrate.ShadowArchitecture.Raven.PhaseTransition.Monotone.PriorAelMonotone
--
-- Defines: prior-añelē?-monotone
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.ShadowArchitecture.Raven.PhaseTransition.Monotone; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.ShadowArchitecture.Raven.PhaseTransition.Monotone.PriorAelMonotone where

open import Substrate.Foundation.Bool.Bool
open import Substrate.Foundation.Bool.Or
open import Substrate.Foundation.Fin.Fin
open import Substrate.Foundation.Fin.To
open import Substrate.Foundation.Nat.Nat
-- ⚑ THE BAN SWEEP DROPPED A `renaming (_≤_ to _ℕ≤_)` WITHOUT REBINDING, leaving
-- `ℕ≤` unbound at :29 — the same signature as the `_+F_` casualties in
-- `InsertionParity` and `OrientationRigCatPermSignChirality`. `ℕ≤` has NO definer
-- anywhere (`agda_defs ℕ≤` → none), which is the tell that it was an alias rather
-- than a name. Foundation's canonical spelling is `_≤_`; it is not renamed at
-- source for one consumer, so the use site takes the real spelling instead.
open import Substrate.Foundation.Nat.Le
open import Substrate.Foundation.Vec
open import Substrate.ShadowArchitecture.Raven.Grammar
open import Substrate.ShadowArchitecture.Raven.PhaseTransition.IsAñeléTerminal
open import Substrate.ShadowArchitecture.Raven.PhaseTransition.PriorAñelé
open import Substrate.Foundation.Eq
open import Substrate.ShadowArchitecture.Raven.PhaseTransition.Monotone.OrMonotoneRight



prior-añelē?-monotone :
  ∀ {n} (v : Vec Stanza n) (i j : Fin n) →
  (toℕ i ≤ toℕ j) →
  prior-añelē? v i ≡ true →
  prior-añelē? v j ≡ true
prior-añelē?-monotone (s ∷ ss) zero    zero    _       ()
prior-añelē?-monotone (s ∷ ss) zero    (suc j) _       ()
prior-añelē?-monotone (s ∷ ss) (suc i) (suc j) (s≤s p) hyp =
  ∨-monotone-right (is-añelē-terminal s)
    (prior-añelē?-monotone ss i j p)
    hyp
