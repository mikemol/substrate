------------------------------------------------------------------------
-- Substrate.Groups.Coxeter.Cyclic.Inverse.InvCanonical
--
-- Defines: inv-canonical
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.Groups.Coxeter.Cyclic.Inverse; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

-- ⚑ ABOVE THE HEADER because the telescope names these types;
-- an import below the header binds nothing for the header itself.
open import Substrate.Foundation.Nat.Nat
open import Substrate.Foundation.Fin.Fin
open import Substrate.Foundation.Eq
open import Substrate.Foundation.Eq.Sym
open import Substrate.Foundation.Eq.Subst
module Substrate.Groups.Coxeter.Cyclic.Inverse.InvCanonical (n : ℕ) where

open import Substrate.Groups.Coxeter.Cyclic.Base n
-- ⛑ the `Base` LEAVES this module cites, derived by
-- `rewire_fcr --siblings Substrate.Groups.Coxeter.Cyclic.Base <file>` — a SET, not a prefix.
-- `Base`'s re-opens are bare (Ⓡ1), so a leaf-defined name no
-- longer arrives through the root. Each leaf carries its OWN minimal
-- telescope, so the argument lists differ by leaf and are read from
-- each header.
open import Substrate.Groups.Coxeter.Cyclic.Base.CanonicalAt n
-- ⚑ `…Cyclic.Bridge n` DROPPED (Ⓑ2c-BRIDGE10″).  Dissolved by 771283c8 into one
-- leaf per theorem, and this file used none of them — the body needs `Fin`,
-- `Canonical-at`, `c-here`, `subst`, `sym`, which arrived through Bridge's
-- `open import …Base n public` CONDUIT.  `Base` is imported directly above and
-- the Foundation names are now bound at their homes, so the line goes entirely.
-- ⚑ SIBLINGS APPLIED: the telescope repair gave these three their `(n : ℕ)` back.
open import Substrate.Groups.Coxeter.Cyclic.Inverse.InvPos n
open import Substrate.Groups.Coxeter.Cyclic.Inverse.Inv n
open import Substrate.Groups.Coxeter.Cyclic.Inverse.InvPowerEq n



inv-canonical : ∀ {w} {k : Fin (suc n)} → Canonical-at w k → Canonical-at (inv w) (inv-pos k)
inv-canonical (c-here k) =
  subst (λ w → Canonical-at w (inv-pos k)) (sym (inv-power-eq k)) (c-here (inv-pos k))
