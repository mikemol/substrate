------------------------------------------------------------------------
-- Substrate.Lifecycle.Fragment.IsReflection
--
-- Defines: promote-Reflection
-- ⟡cap-128-forcing: one lemma, one elaboration unit.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Lifecycle.Fragment.IsReflection where

open import Substrate.Foundation.Eq
open import Substrate.Lifecycle.Fragment
open import Substrate.Lifecycle.Fragment.IRInstance
open import Substrate.Lifecycle.Fragment.Occurrence
open import Substrate.Lifecycle.Fragment.Skeleton
open import Substrate.Lifecycle.Reflection
open import Substrate.WitnessTower.GradeMapInvariant


------------------------------------------------------------------------
-- THE BRIDGE: an IR-retraction IS a lifecycle Reflection.
--
-- ⚑⚑⚑ THIS EDGE DID NOT EXIST, AND ITS ABSENCE IS THE WHOLE FINDING. Two
-- structures were already proved in this tree and neither knew about the
-- other:
--
--   · `Substrate.Algebra.Quotient.IRRetraction.IR` — skeleton + residue,
--     round-trip, and `ir-Canonical` via `split-Canonical`. Built for the jea
--     IR→source extruder. **Zero importers.**
--   · `Substrate.Lifecycle.Reflection` — one field, `round-trip`, consumed by
--     `Drainable` to license the drain. **Its `project` is a bound variable;
--     nothing ever supplied one.**
--
-- They are each other's missing half: `Reflection project reconstruct` has
-- field `reconstruct (project s) ≡ s`, and `IR` proves `recon (decompose s) ≡ s`.
-- The same proposition, written twice, in two subtrees, by two arcs. A search
-- for `IR-Reflection` / `ir-Reflection` / `IR→Reflection` returned **0 names**
-- before this module.
--
-- ⚑ AND THE REUSE INDEX WOULD HAVE HIDDEN IT. `catalog/reuse-index.md` lists
-- `Canonical` at the dissolved parent `Substrate.Algebra.Quotient` and has NO
-- row for `split-Canonical`, `IRRetraction`, `Reflection`, or `Drainable` —
-- because `gen_reuse_index.py` currently crashes (`reuse_catalog.py` uses a
-- bare `sys` while importing `sys as _sys`) behind an advisory `|| true`, so
-- it fails silently and the index simply stops updating. A plan citing the
-- index alone concludes the generator does not exist. `agda_defs.py` is the
-- authority; a stale derived view is not evidence of absence.
--
-- ⚑ WHAT THIS BUYS, CONCRETELY: `drainable` becomes applicable. Its statement
-- is *given a Reflection, two staged records with the same durable image are
-- equal* — i.e. `project` is injective, which is exactly the property the
-- drain needs and exactly the property the skeleton ALONE does not have.
------------------------------------------------------------------------

module _
  (Id : Set)
  (lower   : Staged Id → Skeleton Id)
  (capture : Staged Id → Residue Id)
  (extrude : Skeleton Id → Residue Id → Staged Id)
  (round-trip : (s : Staged Id) → extrude (lower s) (capture s) ≡ s)
  where

  open Promote Id lower capture extrude round-trip

  -- The promote, packaged as the record `Drainable` consumes.
  promote-Reflection : Reflection promote rebuild
  promote-Reflection = reflection rebuild-promote
