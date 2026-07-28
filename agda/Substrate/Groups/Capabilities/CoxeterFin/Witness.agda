------------------------------------------------------------------------
-- Substrate.Groups.Capabilities.CoxeterFin.Witness
--
-- ⟡witness-orbit-collapse. `_orbit_def` proves the five Zₙ witnesses share ONE
-- type_key (one type-level shape) while carrying five DISTINCT graded_keys —
-- one type-orbit, five proof points separated by the cyclic index. So the
-- index is the residue, and parameterizing over it CARRIES that residue
-- rather than discarding it (a text-level "identical modulo index" compare
-- erases exactly the thing that distinguishes the graded points).
--
-- Carrier-locality holds by construction: ONE carrier, `Gen` at index `n`.
-- The capability's ORDER is `suc n` (Z₂ = order 2 at cyclic index 1).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

open import Substrate.Foundation.Nat using (ℕ; suc)

open import Substrate.Algebra.Nat.CyclicSuc using (cyclic-suc)
open import Substrate.Groups.Capabilities.CoxeterFin using (CoxeterFinCapability; from-coxeter-fin-data)
module Substrate.Groups.Capabilities.CoxeterFin.Witness (n : ℕ) where

open import Substrate.Groups.Coxeter.Cyclic.Base n using (Gen; a; insert; σ-OrderOf)
open import Substrate.Groups.Coxeter.Cyclic.Existential n using (Canonical-ex; insert-canonical-ex)
open import Substrate.Groups.Coxeter.Fin-from-Cyclic n using (Fin-to-canonical-ex; action-of-a-is-σ-ex; canonical-to-Fin-ex)


cap : CoxeterFinCapability Gen Canonical-ex (suc n)
cap = from-coxeter-fin-data Gen Canonical-ex
  a insert insert-canonical-ex
  canonical-to-Fin-ex Fin-to-canonical-ex
  cyclic-suc action-of-a-is-σ-ex
  σ-OrderOf
