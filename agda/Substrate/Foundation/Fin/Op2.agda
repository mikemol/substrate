------------------------------------------------------------------------
-- Substrate.Foundation.Fin.Op2
--
-- Defines: _<ᶠ_
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.Foundation.Fin; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Foundation.Fin.Op2 where

open import Substrate.Foundation.Nat.Nat
open import Substrate.Foundation.Nat.Le
open import Substrate.Foundation.Nat.Lt
open import Substrate.Foundation.Fin.Fin
open import Substrate.Foundation.Fin.To


------------------------------------------------------------------------
-- Order on Fin: lift from ℕ via toℕ.
--
-- ⚑ THE BODY SPELLED THE ℕ ORDER `<ℕ` AND NOTHING PROVIDED IT. That name only
-- exists under a `renaming`, which the ban ratchet forbids on a Substrate import
-- — so the horizontal split out of `Substrate.Foundation.Fin` dropped the rename
-- and left the body naming an operator no import supplies (`[NotInScope]`).
--
-- ⚑ A BARE IMPORT ALONE IS NOT ENOUGH — IT GIVES `ClashingDefinition`. Agda will
-- disambiguate a USE by type, but it refuses to DEFINE `_<_` while an imported
-- `_<_` is in scope (measured: *"Multiple definitions of _<_. Previous definition
-- at Substrate/Foundation/Nat/Lt.agda:19"*). Type-directed resolution covers uses,
-- never a new definition of the same name.
--
-- ⚑⚑ SO THE FIN ORDER IS RENAMED AT SOURCE — the only ban-compliant fix, per the
-- ⟡ban-decompose playbook: not a `using` filter, not a qualifier, not an alias.
-- The provider was ALREADY decomposed (`Nat.Lt` is a one-definition leaf), so this
-- is a collision that SURVIVED decomposition, which is the case where renaming is
-- correct rather than premature.
--
-- ⚑ `Nat.Le` IS IMPORTED TOO because `Nat.Lt`'s `_<_` is defined in terms of `_≤_`;
-- `Substrate.Foundation.Fin.From2` carries the same pair for the same reason, and
-- `Nat.Lt` has 161 external importers, every one of them bare.
------------------------------------------------------------------------

_<ᶠ_ : {n : ℕ} → Fin n → Fin n → Set
i <ᶠ j = toℕ i < toℕ j
