------------------------------------------------------------------------
-- Substrate.Groups.Coxeter.Cyclic.Bridge.InsertPowerEq
--
-- Defines: insert-power-eq
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.Groups.Coxeter.Cyclic.Bridge; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

-- ⚑ TELESCOPE RECOVERED FROM THE RETIRED PARENT @771283c8~1 (`Bridge (n : ℕ)`).
-- ⚑ AND THE TWO SIBLING IMPORTS ARE APPLIED, since they regained the same
-- telescope in this pass — an unapplied one elaborates at a fresh metavariable
-- and fails as `[UnequalTerms]` rather than as a scope error.
open import Substrate.Foundation.Nat.Nat
open import Substrate.Foundation.Negation.Dec
open import Substrate.Foundation.Eq
open import Substrate.Foundation.Fin.Fin
open import Substrate.Foundation.Fin.To
open import Substrate.Foundation.Nat.Lt2

module Substrate.Groups.Coxeter.Cyclic.Bridge.InsertPowerEq (n : ℕ) where

open import Substrate.Groups.Coxeter.Cyclic.Base n
-- ⛑ Ⓡ2ᵈ: the `Defs` LEAVES this shard cites, derived by
-- `rewire_fcr --siblings Defs <file>` — a SET, not a prefix. `Defs`'s
-- re-opens are bare (Ⓡ1), so a leaf-defined name no longer arrives
-- through the root. Each leaf carries its OWN minimal telescope, so the
-- argument lists differ by leaf and are read from each header.
open import Substrate.Groups.Coxeter.Cyclic.Base.Insert n
open import Substrate.Groups.Coxeter.Cyclic.Base.Op n
open import Substrate.Groups.Coxeter.Cyclic.Base.Power
open import Substrate.Groups.Coxeter.Cyclic.Bridge.InsertPowerEqYes n
open import Substrate.Groups.Coxeter.Cyclic.Bridge.InsertPowerEqNo n



insert-power-eq : (k : Fin (suc n)) →
                  insert a (power (toℕ k)) ≡ power (toℕ (σ k))
insert-power-eq k with toℕ k <? n
... | yes p  = insert-power-eq-yes k p
... | no  ¬p = insert-power-eq-no k ¬p
