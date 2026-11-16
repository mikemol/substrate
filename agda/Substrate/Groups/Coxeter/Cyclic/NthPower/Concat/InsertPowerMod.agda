------------------------------------------------------------------------
-- Substrate.Groups.Coxeter.Cyclic.NthPower.Concat.InsertPowerMod
--
-- Defines: insert-power-mod
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.Groups.Coxeter.Cyclic.NthPower.Concat; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

-- ⚑ ABOVE THE HEADER because the telescope names these types;
-- an import below the header binds nothing for the header itself.
open import Substrate.Foundation.Nat.Nat
open import Substrate.Foundation.Fin.From2
open import Substrate.Foundation.Fin.Properties
open import Substrate.Foundation.Eq
open import Substrate.Foundation.Eq.Sym
open import Substrate.Foundation.Eq.Trans
open import Substrate.Foundation.Eq.Cong
open import Substrate.Foundation.Eq.Subst
open import Substrate.Foundation.Nat.Nat.ModSuc
open import Substrate.Algebra.Nat.Mod.ModSucBound
open import Substrate.Algebra.Nat.Mod.ModSucId
open import Substrate.Algebra.Nat.Mod.ModSucPeriodic
open import Substrate.Algebra.Nat.Mod.ModSucSuc
open import Substrate.Algebra.Nat.Mod.SucModSucLt
open import Substrate.Algebra.Nat.Mod.SucModSucSelf
open import Substrate.Algebra.Nat.CyclicSuc
module Substrate.Groups.Coxeter.Cyclic.NthPower.Concat.InsertPowerMod (n : ℕ) where

-- ⚑ `…Cyclic.Bridge n` REWIRED, not dropped (Ⓑ2c-BRIDGE10″).  Unlike the Inverse
-- leaves, this file uses a REAL Bridge theorem — `insert-power-eq` at :27 — so it
-- takes that leaf rather than losing the import.  The rest of what the bare
-- import supplied was the `…Base n public` conduit, and `Base` is imported below.
open import Substrate.Groups.Coxeter.Cyclic.Bridge.InsertPowerEq n
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


insert-power-mod : (k : ℕ) →
                  insert a (power (k mod-suc n)) ≡ power ((suc k) mod-suc n)
insert-power-mod k =
  subst (λ x → insert a (power x) ≡ power ((suc k) mod-suc n))
        (toℕ-fromℕ< (mod-suc-bound k n))
        (trans (insert-power-eq (fromℕ< (mod-suc-bound k n)))
               (cong power
                 (trans (cyclic-suc-toℕ (fromℕ< (mod-suc-bound k n)))
                 (trans (cong (λ x → (suc x) mod-suc n)
                              (toℕ-fromℕ< (mod-suc-bound k n)))
                        (sym (mod-suc-suc k n))))))
