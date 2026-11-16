------------------------------------------------------------------------
-- Substrate.Groups.Coxeter.Cyclic.Bridge.InsertCanonical
--
-- Defines: insert-canonical
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.Groups.Coxeter.Cyclic.Bridge; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

-- ⚑ TELESCOPE RECOVERED FROM THE RETIRED PARENT @771283c8~1 (`Bridge (n : ℕ)`);
-- the sibling import is applied for the same reason as its own siblings'.
open import Substrate.Foundation.Nat.Nat
open import Substrate.Foundation.Eq
open import Substrate.Foundation.Eq.Subst
open import Substrate.Foundation.Eq.Sym
open import Substrate.Groups.Coxeter.Word
open import Substrate.Foundation.Fin.Fin
open import Substrate.Groups.Coxeter.Cyclic.Base.CanonicalAt
open import Substrate.Groups.Coxeter.Cyclic.Base.Gen

module Substrate.Groups.Coxeter.Cyclic.Bridge.InsertCanonical (n : ℕ) where

open import Substrate.Groups.Coxeter.Cyclic.Base n
-- ⛑ Ⓡ2ᵈ: the `Defs` LEAVES this shard cites, derived by
-- `rewire_fcr --siblings Defs <file>` — a SET, not a prefix. `Defs`'s
-- re-opens are bare (Ⓡ1), so a leaf-defined name no longer arrives
-- through the root. Each leaf carries its OWN minimal telescope, so the
-- argument lists differ by leaf and are read from each header.
open import Substrate.Groups.Coxeter.Cyclic.Base.Insert n
open import Substrate.Groups.Coxeter.Cyclic.Base.Op n
open import Substrate.Groups.Coxeter.Cyclic.Bridge.InsertPowerEq n



------------------------------------------------------------------------
-- insert-canonical at the Fin-indexed level.
------------------------------------------------------------------------

insert-canonical : (g : Gen) {w : Word Gen} {k : Fin (suc n)} →
                   Canonical-at w k → Canonical-at (insert g w) (σ k)
insert-canonical a (c-here k) =
  subst (λ w → Canonical-at w (σ k)) (sym (insert-power-eq k)) (c-here (σ k))
