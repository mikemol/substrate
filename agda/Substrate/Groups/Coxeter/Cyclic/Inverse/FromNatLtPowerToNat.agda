------------------------------------------------------------------------
-- Substrate.Groups.Coxeter.Cyclic.Inverse.FromNatLtPowerToNat
--
-- Defines: fromℕ<-power-toℕ
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.Groups.Coxeter.Cyclic.Inverse; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

-- ⚑ ABOVE THE HEADER because the telescope names these types;
-- an import below the header binds nothing for the header itself.
open import Substrate.Foundation.Nat.Nat
open import Substrate.Foundation.Nat.Lt
open import Substrate.Foundation.Fin.Fin
open import Substrate.Foundation.Fin.To
open import Substrate.Foundation.Fin.From2
open import Substrate.Foundation.Eq
open import Substrate.Groups.Coxeter.Word.Length
module Substrate.Groups.Coxeter.Cyclic.Inverse.FromNatLtPowerToNat (n : ℕ) where

open import Substrate.Groups.Coxeter.Cyclic.Base n
-- ⛑ Ⓡ2ᵈ: the `Defs` LEAVES this shard cites, derived by
-- `rewire_fcr --siblings Defs <file>` — a SET, not a prefix. `Defs`'s
-- re-opens are bare (Ⓡ1), so a leaf-defined name no longer arrives
-- through the root. Each leaf carries its OWN minimal telescope, so the
-- argument lists differ by leaf and are read from each header.
open import Substrate.Groups.Coxeter.Cyclic.Base.LengthPower
open import Substrate.Groups.Coxeter.Cyclic.Base.Power
-- ⚑ `…Cyclic.Bridge n` DROPPED (Ⓑ2c-BRIDGE10″) — pure conduit; `Base` above
-- supplies `power`/`length-power`.  ⚑ Sibling APPLIED, post-telescope-repair.
open import Substrate.Groups.Coxeter.Cyclic.Inverse.FromNatLtToNatId n


fromℕ<-power-toℕ : (k : Fin (suc n))
                 → (p : length (power (toℕ k)) < suc n)
                 → fromℕ< p ≡ k
fromℕ<-power-toℕ k p
  rewrite length-power (toℕ k) = fromℕ<-toℕ-id k p
