------------------------------------------------------------------------
-- Substrate.Linguistic.ClosureLog
--
-- D9 of the Closure-debt arc per [scratch/closure_arc_plan.md].
--
-- Substrate-native bookkeeping for the D-arc closures: a Vec of
-- records, each documenting one deferred item the D-arc closed
-- and the slice that closed it. Useful for future arcs that want
-- to query "is X still deferred?" at the substrate-internal layer
-- rather than reading scratch/ plan files.
--
-- Per [[feedback-minimize-stdlib-deps]]-strengthened: enums
-- (DeferredItem, ClosureSlice) instead of String fields.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Linguistic.ClosureLog where

open import Substrate.Foundation.Nat using (ℕ)
open import Substrate.Foundation.Vec using (Vec; []; _∷_)

------------------------------------------------------------------------
-- 1. DeferredItem enum.
--
-- The ten items the D-arc closed (one per D-slice).
------------------------------------------------------------------------

data DeferredItem : Set where
  WithBasisAction-stub          : DeferredItem  -- T4
  Kelen-relation-composition    : DeferredItem  -- C5
  Lie-anti-commutativity        : DeferredItem  -- C7 axiom #1
  Lie-Jacobi-identity           : DeferredItem  -- C7 axiom #2
  Solresol-transposition-lift   : DeferredItem  -- C4 universal property
  Lojban-AsCCC-parent-deferral  : DeferredItem  -- L10 prose
  TokiPona-AsLinearBridge-deferral : DeferredItem  -- T10 prose
  Six-witness-alignment-summary    : DeferredItem  -- aggregate
  Closure-log-bookkeeping          : DeferredItem  -- this file
  Regression-capstone              : DeferredItem  -- D10

------------------------------------------------------------------------
-- 2. ClosureSlice enum.
--
-- The ten D-arc slices, each closing exactly one deferred item.
------------------------------------------------------------------------

data ClosureSlice : Set where
  D1 D2 D3 D4 D5 D6 D7 D8 D9 D10 : ClosureSlice

------------------------------------------------------------------------
-- 3. The ClosureEntry record.
------------------------------------------------------------------------

record ClosureEntry : Set where
  constructor mkEntry
  field
    item  : DeferredItem
    slice : ClosureSlice

open ClosureEntry public

------------------------------------------------------------------------
-- 4. The closure log.
--
-- Ten entries, one per D-arc slice, recording the deferred item
-- it closed. The order matches the D-arc execution order.
------------------------------------------------------------------------

closure-log : Vec ClosureEntry 10
closure-log =
  mkEntry WithBasisAction-stub             D1 ∷
  mkEntry Kelen-relation-composition       D2 ∷
  mkEntry Lie-anti-commutativity           D3 ∷
  mkEntry Lie-Jacobi-identity              D4 ∷
  mkEntry Solresol-transposition-lift      D5 ∷
  mkEntry Lojban-AsCCC-parent-deferral     D6 ∷
  mkEntry TokiPona-AsLinearBridge-deferral D7 ∷
  mkEntry Six-witness-alignment-summary    D8 ∷
  mkEntry Closure-log-bookkeeping          D9 ∷
  mkEntry Regression-capstone              D10 ∷
  []

------------------------------------------------------------------------
-- 5. Closure count.
------------------------------------------------------------------------

closure-count : ℕ
closure-count = 10

------------------------------------------------------------------------
-- 6. Capstone.
--
-- `closure-log` is the substrate-native record of what the D-arc
-- closed. Downstream tools (or future arcs adding more closures)
-- can extend this log mechanically.
------------------------------------------------------------------------
