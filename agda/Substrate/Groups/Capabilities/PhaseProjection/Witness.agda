------------------------------------------------------------------------
-- Substrate.Groups.Capabilities.PhaseProjection.Witness
--
-- ⟡witness-orbit-collapse. The five Zₙ witnesses of PhaseProjection had byte-identical
-- bodies differing ONLY in the cyclic index — a pure index orbit, visible
-- only in the CANONICAL (conduit-free) form: all five demand the same
-- elaborated leaves, and only the module application varies.
--
-- The orbit is the object. The cyclic family is already parameterized by the
-- index, so parameterizing the witness over the SAME index collapses 5
-- modules into 1 and gives carrier-locality by construction: ONE carrier,
-- `Gen` at index `n`. Each Zₙ is an APPLICATION, not a copy.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

open import Substrate.Foundation.Nat using (ℕ)

open import Substrate.Groups.Coxeter.Word using (Word)
import Substrate.Groups.FreeCyclic-Coxeter as F   -- the SECOND carrier (a definer, not a conduit)
open import Substrate.Groups.Capabilities.PhaseProjection using (from-coxeter-data)
module Substrate.Groups.Capabilities.PhaseProjection.Witness (n : ℕ) where

open import Substrate.Groups.Coxeter.Cyclic.Base n using (Gen; insert)
open import Substrate.Groups.Coxeter.Cyclic.Existential n using (Canonical-ex; c-ε; insert-canonical-ex; normalize)


cap = from-coxeter-data Gen normalize
