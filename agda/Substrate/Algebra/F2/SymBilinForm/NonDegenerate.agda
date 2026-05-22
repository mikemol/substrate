------------------------------------------------------------------------
-- Substrate.Algebra.F2.SymBilinForm.NonDegenerate
--
-- NonDegenerate M : the radical contains only 𝟎ⱽ. The kernel-free
-- predicate expressed via categorical primitives (Wide-Meet of
-- IsEqualised); same structure at any n.
--
-- The kernel-free witness for metric-id at generic n lives at:
--   NonDegenerate.BasisRowEqMetricId    — lookup (basis i) j ≡ metric-id i j
--   NonDegenerate.PairMetricIdWithBasis — pairing extracts component
--   NonDegenerate.MetricIdNonDegenerate — the theorem
--
-- The submodules are NOT re-exported here to avoid a cycle (they
-- transitively depend on HodgeRecast, which transitively depends on
-- the parent SymBilinForm aggregator, which would form a loop).
-- Consumers import the specific submodule they need.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.F2.SymBilinForm.NonDegenerate where

open import Substrate.Foundation.Eq using (_≡_)
open import Substrate.Algebra.F2.Vector using (Vector; 𝟎ⱽ)
open import Substrate.Algebra.F2.SymBilinForm.BilinForm using (BilinForm)
open import Substrate.Algebra.F2.SymBilinForm.Radical using (Radical)

NonDegenerate : ∀ {n} → BilinForm n → Set
NonDegenerate {n} M = (v : Vector n) → Radical M v → v ≡ 𝟎ⱽ
