------------------------------------------------------------------------
-- Substrate.Foundation.Fin.Op3
--
-- Defines: _≤ᶠ_
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.Foundation.Fin; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Foundation.Fin.Op3 where

open import Substrate.Foundation.Nat.Nat
open import Substrate.Foundation.Nat.Le
open import Substrate.Foundation.Fin.Fin
open import Substrate.Foundation.Fin.To


------------------------------------------------------------------------
-- Order on Fin: lift from ℕ via toℕ. The `Op2` sibling's ⚑ block carries the
-- full reasoning; the short form:
--
-- ⚑ THE BODY SPELLED THE ℕ ORDER `≤ℕ` AND NOTHING PROVIDED IT — a name that only
-- exists under a `renaming`, which the ban ratchet forbids on a Substrate import.
-- The horizontal split out of `Substrate.Foundation.Fin` dropped the rename and
-- left the body naming an operator no import supplies (`[NotInScope]`).
--
-- ⚑ A BARE IMPORT ALONE GIVES `ClashingDefinition`: Agda disambiguates a USE by
-- type but refuses to DEFINE `_≤_` while an imported `_≤_` is in scope. So the Fin
-- operator is renamed AT SOURCE — the only ban-compliant fix, and correct here
-- rather than premature because the provider (`Nat.Le`, a one-definition leaf) is
-- ALREADY decomposed: this is a collision that SURVIVED decomposition.
--
-- ⚑ RENAMED BY HAND, NOT BY `rename_at_source.py`, DELIBERATELY. On `Op2` that
-- tool rewrote the definition AND the ℕ use on the right-hand side — its own
-- measured 1-in-10 false positive, firing in the home file where it applies no
-- ambiguity check at all (it guards IMPORTERS, not the definition site). It also
-- substituted inside comment prose. Two lines did not justify the recovery.
------------------------------------------------------------------------

_≤ᶠ_ : {n : ℕ} → Fin n → Fin n → Set
i ≤ᶠ j = toℕ i ≤ toℕ j
