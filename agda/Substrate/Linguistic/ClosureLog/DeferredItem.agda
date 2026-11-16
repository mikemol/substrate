------------------------------------------------------------------------
-- Substrate.Linguistic.ClosureLog.DeferredItem
--
-- Defines: Closure-log-bookkeeping, DeferredItem, Kelen-relation-composition, Lie-Jacobi-identity, Lie-anti-commutativity, Lojban-AsCCC-parent-deferral, Regression-capstone, Six-witness-alignment-summary, Solresol-transposition-lift, TokiPona-AsLinearBridge-deferral, WithBasisAction-stub
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.Linguistic.ClosureLog; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Linguistic.ClosureLog.DeferredItem where




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
