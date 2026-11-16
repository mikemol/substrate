------------------------------------------------------------------------
-- Substrate.Groups.Coxeter.Cyclic.Inverse.Inv
--
-- Defines: inv
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.Groups.Coxeter.Cyclic.Inverse; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

-- ⚑⚑ THESE IMPORTS SIT ABOVE THE MODULE HEADER BECAUSE THE TELESCOPE NEEDS THEM.
-- `module … (n : ℕ) where` mentions `ℕ`, and an import BELOW the header binds
-- nothing for the header itself — agda reports `NotInScope: ℕ` at the telescope's
-- own column.  The dissolved `Bridge` conduit used to supply `ℕ`/`Fin`/`toℕ`
-- transitively (its body was `open import …Base n public`), so no shard ever
-- imported them; restoring the telescope makes that dependency load-bearing and
-- visible at once, which is the detangling the cap is forcing.
open import Substrate.Foundation.Nat.Nat
open import Substrate.Foundation.Fin.Fin
open import Substrate.Foundation.Fin.To
open import Substrate.Foundation.Fin.From2
open import Substrate.Foundation.Nat.Properties.Order
open import Substrate.Foundation.Nat.Lt2
open import Substrate.Foundation.Negation.Dec
open import Substrate.Groups.Coxeter.Word
open import Substrate.Groups.Coxeter.Word.Length
open import Substrate.Groups.Coxeter.Cyclic.Base.Gen

module Substrate.Groups.Coxeter.Cyclic.Inverse.Inv (n : ℕ) where

open import Substrate.Groups.Coxeter.Cyclic.Base n
-- ⛑ Ⓡ2ᵈ: the `Defs` LEAVES this shard cites, derived by
-- `rewire_fcr --siblings Defs <file>` — a SET, not a prefix. `Defs`'s
-- re-opens are bare (Ⓡ1), so a leaf-defined name no longer arrives
-- through the root. Each leaf carries its OWN minimal telescope, so the
-- argument lists differ by leaf and are read from each header.
open import Substrate.Groups.Coxeter.Cyclic.Base.Power
-- ⚑ WAS a bare `open import …Cyclic.Bridge n` (Ⓑ2c-BRIDGE10) — a module the
-- ban-decompose commit (771283c8) dissolved into one leaf per theorem.  The
-- split ran and the REWIRE did not, so this named a module with no file.
-- ⚑ A BARE import of the old Bridge also took everything it RE-EXPORTED: its
-- body was `open import …Cyclic.Base n public`, which is where `power`/`length`
-- and the Fin machinery below arrived from.  `Base` is already imported above,
-- so nothing here needs a Bridge leaf — this file used the CONDUIT, not the
-- theorems.  Dropping the import is the whole repair.
-- ⚑ APPLIED, because the telescope repair gave `InvPos` its `(n : ℕ)` back.  A
-- sibling reference that was unapplied while BOTH lacked telescopes has to gain
-- the argument when they regain them — the two halves of the same defect.
open import Substrate.Groups.Coxeter.Cyclic.Inverse.InvPos n



------------------------------------------------------------------------
-- inv: Word-level inverse via length-check + power composition.
------------------------------------------------------------------------

inv : Word Gen → Word Gen
inv w with length w <? suc n
... | yes p = power (toℕ (inv-pos (fromℕ< p)))
... | no  _ = w
