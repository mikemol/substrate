------------------------------------------------------------------------
-- Substrate.FUSep.FUSepQConfluence.Iso
--
-- Defines: Iso, bwd, bwd∘fwd, fwd, fwd∘bwd
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.FUSep.FUSepQConfluence; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K --guardedness #-}

module Substrate.FUSep.FUSepQConfluence.Iso where

open import Substrate.Foundation.Product
import Substrate.Foundation.Product as FP   -- for the ⟡def-eq projection witnesses
open import Substrate.Foundation.Nat.Nat
open import Substrate.Foundation.Eq



------------------------------------------------------------------------
-- A WedgeIso, inlined (Wedge/Iso shape): a bidirectional map with round-trips.
------------------------------------------------------------------------
record Iso (A B : Set) : Set where
  field
    fwd     : A → B
    bwd     : B → A
    bwd∘fwd : (a : A) → bwd (fwd a) ≡ a
    fwd∘bwd : (b : B) → fwd (bwd b) ≡ b
open Iso public

------------------------------------------------------------------------
-- THE TWO INDEXES over the shared node bucket Tm. An index is a hierarchical
-- edge set: at a node, a backpointer (the residue/witness from ADD 106) + the
-- child node. `RIdx` (reduce) and `PIdx` (peel) index the SAME Tm bucket.
--   RIdx s = (parent-backpointer, reduct)   -- reduce edge: lossy, parent kept
--   PIdx s = (argument-residue, function)   -- peel edge: structure, recomputable
-- Both are (Wit × Tm) — the shared shape — differing only in the recon they feed.
------------------------------------------------------------------------
RIdx PIdx : Set
