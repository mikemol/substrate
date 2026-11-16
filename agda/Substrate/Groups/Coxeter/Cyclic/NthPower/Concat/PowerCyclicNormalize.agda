------------------------------------------------------------------------
-- Substrate.Groups.Coxeter.Cyclic.NthPower.Concat.PowerCyclicNormalize
--
-- Defines: power-cyclic-normalize
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.Groups.Coxeter.Cyclic.NthPower.Concat; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

-- ⚑ ABOVE THE HEADER because the telescope names these types;
-- an import below the header binds nothing for the header itself.
open import Substrate.Foundation.Nat.Nat
open import Substrate.Foundation.Eq
open import Substrate.Foundation.Eq.Trans
open import Substrate.Foundation.Nat.Nat.ModSuc
open import Substrate.Algebra.Nat.Mod.ModSucBound
open import Substrate.Algebra.Nat.Mod.ModSucId
open import Substrate.Algebra.Nat.Mod.ModSucPeriodic
open import Substrate.Algebra.Nat.Mod.ModSucSuc
open import Substrate.Algebra.Nat.Mod.SucModSucLt
open import Substrate.Algebra.Nat.Mod.SucModSucSelf
open import Substrate.Groups.Coxeter.Cyclic.Base.Gen
module Substrate.Groups.Coxeter.Cyclic.NthPower.Concat.PowerCyclicNormalize (n : ℕ) where

-- ⚑ `…Cyclic.Bridge n` DROPPED (Ⓑ2c-BRIDGE10″) — pure conduit; the body composes
-- two sibling lemmas and needs only `normalize`/`power` from Core/Base.
-- ⚑ ORDER: Base, Existential, THEN the application consuming both.
open import Substrate.Groups.Coxeter.Cyclic.Base n
-- ⛑ Ⓡ2ᵈ: the `Defs` LEAVES this shard cites, derived by
-- `rewire_fcr --siblings Defs <file>` — a SET, not a prefix. `Defs`'s
-- re-opens are bare (Ⓡ1), so a leaf-defined name no longer arrives
-- through the root. Each leaf carries its OWN minimal telescope, so the
-- argument lists differ by leaf and are read from each header.
open import Substrate.Groups.Coxeter.Cyclic.Base.Insert n
open import Substrate.Groups.Coxeter.Cyclic.Base.Power
open import Substrate.Groups.Coxeter.Cyclic.Existential n
open import Substrate.Groups.Coxeter.ListPresentation
  Gen Canonical-ex c-ε insert insert-canonical-ex
open import Substrate.Groups.Coxeter.Cyclic.Core n
open import Substrate.Groups.Coxeter.Cyclic.NthPower.Concat.Private n
open import Substrate.Groups.Coxeter.Cyclic.NthPower.Concat.NormalizePower n
open import Substrate.Groups.Coxeter.Cyclic.NthPower.Concat.IterPowerMod n



power-cyclic-normalize : (k : ℕ) → normalize (power k) ≡ power (k mod-suc n)
power-cyclic-normalize k = trans (normalize-power k) (iter-power-mod k)
