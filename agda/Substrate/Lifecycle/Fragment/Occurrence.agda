------------------------------------------------------------------------
-- Substrate.Lifecycle.Fragment.Occurrence
--
-- Defines: Occurrence, Residue
-- ⟡cap-128-forcing: one lemma, one elaboration unit.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Lifecycle.Fragment.Occurrence where

open import Substrate.Foundation.Nat.Nat
open import Substrate.Foundation.List


------------------------------------------------------------------------
-- THE RESIDUE: what the quotient threw away — `IR`'s second carrier.
--
-- This is `obs_node`. For each observation it records WHICH node the
-- observation interned to, and the observation's own child list.
--
-- ⚑⚑ THE `ch` FIELD IS NOT OPTIONAL AND IS NOT RECOVERABLE FROM THE
-- SKELETON. `node_child` holds the children's NODE IDS; `ch` holds the
-- children's LOCAL IDS. Those are different data: the node ids are
-- post-quotient (shared), the local ids are pre-quotient (per-occurrence).
-- Rebuilding an `ekey` needs the local ids, because that is what the source
-- document's `"ch"` array contains. This is exactly why the drain licence
-- carries TWO independent edge conjuncts, reading opposite sides of the
-- wedge: one rebuilds the child list from `obs.ekey` (proving `edge`
-- redundant WITH the staged copy), the other from `obs_node.ch` (proving it
-- recoverable WITHOUT it). Only the second licenses deleting both, and
-- reading the first as covering it is the wedge backwards.
--
-- ⚑ INTERNING IS `recon`, AND THIS IS THE `r`. The substrate already names
-- the shape: `a = recon q b r` — the node is the base, the OCCURRENCE is the
-- residue, and keeping it is what turns a lossy projection into a retraction.
-- `Reflection.agda` puts it as *"converge the key, keep the path back, never
-- a lossy erase"*, and `IRRetraction`'s header, written for a different arc
-- entirely, reaches the identical conclusion: *"byte-grade is structurally
-- impossible was the wrong frame: the residue is the kept cofactor, and
-- keeping it turns the lossy skeleton projection into this retraction."*
-- Two arcs, two problems, one structure — which is why this module
-- instantiates that generator instead of restating it.
--
-- ⚑ A MULTISET, NOT A FUNCTION, AND THE STORE IS EXPLICIT ABOUT IT.
-- `obs_node` is declared with NO primary key, deliberately: a second insert
-- of the same `(core_id, local_id)` DUPLICATES rather than conflicts, and the
-- drain licence's `projected` conjunct is a LEFT JOIN that duplicates along
-- with it. A `List` is therefore the faithful model; a map would assume a
-- uniqueness the schema does not enforce.
------------------------------------------------------------------------

module _ (Id : Set) where

  -- One observation's residue: where it interned, and what it pointed at.
  record Occurrence : Set where
    constructor occurrence
    field
      local : ℕ              -- obs_node.local_id — the occurrence's position
      node  : Id             -- obs_node.node_id  — the class it collapsed into
      ch    : List ℕ         -- obs_node.ch       — its OWN children's local ids

  -- The residue for one core. A multiset: no key is declared upstream.
  Residue : Set
  Residue = List Occurrence
