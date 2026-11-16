------------------------------------------------------------------------
-- Substrate.Groups.Capabilities.CoxeterGroup.Witness
--
-- ⟡witness-orbit-collapse. The five Zₙ witnesses of CoxeterGroup were five
-- files with byte-identical bodies differing ONLY in the cyclic index — a
-- pure index orbit, which the CANONICAL (conduit-free) form made visible:
-- every witness demands the same 20 elaborated leaves, and only the module
-- application varies.
--
-- So the orbit is the object, not its five points. The cyclic family is
-- already parameterized by the index, so parameterizing the witness over
-- the SAME index collapses 5 modules into 1 and satisfies carrier-locality
-- by construction: this module has exactly ONE carrier, `Gen` at index `n`.
--
-- Each Zₙ is then an APPLICATION (`Witness.cap 1` = Z₂), not a copy.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

open import Substrate.Foundation.Nat.Nat

open import Substrate.Foundation.Fin.Fin
open import Substrate.Groups.Coxeter.Word using (++-assoc)
open import Substrate.Groups.Capabilities.CoxeterGroup using (CoxeterGroupCapability)
open import Substrate.Groups.Coxeter.Cyclic.Base.Gen
open import Substrate.Groups.Coxeter.Cyclic.Base.Insert
module Substrate.Groups.Capabilities.CoxeterGroup.Witness (n : ℕ) where

open import Substrate.Groups.Coxeter.Cyclic.Base n
open import Substrate.Groups.Coxeter.Cyclic.Core n using (canonical-is-fixed; insert-append-lemma; normalize-distrib)
-- ⚑ `normalize`/`normalize-canonical` ARE NOT `Existential`'s (Ⓐ¹³) — they are
-- `ListPresentation`'s, reached through Existential's own open.  Agda reported
-- the clause as a WARNING (`ModuleDoesntExport`) and bound nothing.
open import Substrate.Groups.Coxeter.Cyclic.Existential n
open import Substrate.Groups.Coxeter.ListPresentation
  Gen Canonical-ex c-ε insert insert-canonical-ex
open import Substrate.Groups.Coxeter.Cyclic.InvCanonical.Left n using (inv-left-canonical-ex)
open import Substrate.Groups.Coxeter.Cyclic.InvCanonical.Right n using (inv-right-canonical-ex)
-- ⚑ `Cyclic.Inverse` DISSOLVED — `inv` is `Inverse.Inv`'s.
open import Substrate.Groups.Coxeter.Cyclic.Inverse.Inv n using (inv)


cap : CoxeterGroupCapability Gen Canonical-ex
cap = record
  { c-ε                = c-pos zero
  ; ++-assoc           = ++-assoc
  ; normalize          = normalize
  ; normalize-canonical = normalize-canonical
  ; canonical-is-fixed = canonical-is-fixed
  ; normalize-distrib  = normalize-distrib
  ; inv                = inv
  ; inv-canonical      = inv-canonical-ex
  ; inv-left-canonical = inv-left-canonical-ex
  ; inv-right-canonical = inv-right-canonical-ex
  }
