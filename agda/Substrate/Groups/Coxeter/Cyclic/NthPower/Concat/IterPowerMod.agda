------------------------------------------------------------------------
-- Substrate.Groups.Coxeter.Cyclic.NthPower.Concat.IterPowerMod
--
-- Defines: iter-power-mod
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.Groups.Coxeter.Cyclic.NthPower.Concat; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

-- ⚑ ABOVE THE HEADER because the telescope names these types;
-- an import below the header binds nothing for the header itself.
open import Substrate.Foundation.Nat.Nat
open import Substrate.Foundation.Eq
open import Substrate.Foundation.Eq.Trans
open import Substrate.Foundation.Eq.Cong
open import Substrate.Foundation.Nat.Nat.ModSuc
open import Substrate.Algebra.Nat.Mod.ModSucBound
open import Substrate.Algebra.Nat.Mod.ModSucId
open import Substrate.Algebra.Nat.Mod.ModSucPeriodic
open import Substrate.Algebra.Nat.Mod.ModSucSuc
open import Substrate.Algebra.Nat.Mod.SucModSucLt
open import Substrate.Algebra.Nat.Mod.SucModSucSelf
open import Substrate.Groups.Coxeter.Word
module Substrate.Groups.Coxeter.Cyclic.NthPower.Concat.IterPowerMod (n : ℕ) where

-- ⚑ `…Cyclic.Bridge n` DROPPED (Ⓑ2c-BRIDGE10″) — pure conduit here: the body
-- names `iter`/`insert`/`a`/`power`, all from `Base`/`Core` below.
open import Substrate.Groups.Coxeter.Cyclic.Base n
-- ⛑ Ⓡ2ᵈ: the `Defs` LEAVES this shard cites, derived by
-- `rewire_fcr --siblings Defs <file>` — a SET, not a prefix. `Defs`'s
-- re-opens are bare (Ⓡ1), so a leaf-defined name no longer arrives
-- through the root. Each leaf carries its OWN minimal telescope, so the
-- argument lists differ by leaf and are read from each header.
open import Substrate.Groups.Coxeter.Cyclic.Base.Insert n
open import Substrate.Groups.Coxeter.Cyclic.Base.Power
open import Substrate.Groups.Coxeter.Cyclic.Core n
open import Substrate.Groups.Coxeter.Cyclic.NthPower.Concat.Private n
open import Substrate.Groups.Coxeter.Cyclic.NthPower.Concat.InsertPowerMod n



iter-power-mod : (k : ℕ) → iter k (insert a) [] ≡ power (k mod-suc n)
iter-power-mod zero    = refl
iter-power-mod (suc k) =
  trans (cong (insert a) (iter-power-mod k))
        (insert-power-mod k)
