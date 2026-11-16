------------------------------------------------------------------------
-- Substrate.Linguistic.ClosureLog.ClosureLog
--
-- Defines: closure-log
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.Linguistic.ClosureLog; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Linguistic.ClosureLog.ClosureLog where

open import Substrate.Foundation.Vec
open import Substrate.Linguistic.ClosureLog.DeferredItem
open import Substrate.Linguistic.ClosureLog.ClosureSlice
open import Substrate.Linguistic.ClosureLog.ClosureEntry



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
