------------------------------------------------------------------------
-- Substrate.Category.CascadedCoalgebra
--
-- A two-level cascaded coalgebra: an inner coalgebra evolves under
-- a stream of inputs; an outer coalgebra evolves under the inner
-- coalgebra's state. One-way coupling: outer reads inner; inner
-- does NOT read outer.
--
-- Per the DBE constructive-completeness criterion (user 2026-05-21):
-- this record carries (InnerState, OuterState, Input, initial states,
-- per-level step functions). Given these fields, a caller can
-- constructively simulate the cascade from initial states forward
-- under any input stream.
--
-- This is the categorical generalization of the 2nd-order PLL:
-- inner level = phase tracking; outer level = frequency tracking.
-- Per [[multi-route-equivariance-recovery]]: the 2-level cascade
-- supports compositional corpora where the prime-set structure
-- itself drifts (outer tracks "which primes" while inner tracks
-- "phase within the active primes").
--
-- Per [[coalgebraic-not-consumer-driven]]: this is COALGEBRAIC at
-- its lowest level — inner-step and outer-step are unfold operations
-- that expose the gauge structure as the input stream is consumed.
--
-- Categorical name: iterated/cascaded coalgebra. Per
-- [[categorical-name-first]]: use the established name; "2nd-order
-- PLL" is an INSTANCE, not the category.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Category.CascadedCoalgebra where

open import Data.List using (List; []; _∷_; foldl)
open import Substrate.Foundation.Product using (_×_; _,_)
open import Level using (Level) renaming (suc to lsuc)
open import Substrate.Foundation.Eq using (_≡_; refl)

private
  variable
    ℓ : Level

------------------------------------------------------------------------
-- The cascaded coalgebra record.
--
-- One-way coupling: outer-step takes the current OuterState AND
-- the current InnerState (the inner level's observable output);
-- inner-step takes only InnerState and Input (inner does NOT see
-- OuterState).
--
-- The constructive content: caller folds (inner-step, outer-step)
-- over the input stream starting from (initial-inner, initial-outer).

record CascadedCoalgebra : Set (lsuc ℓ) where
  field
    InnerState     : Set ℓ
    OuterState     : Set ℓ
    Input          : Set ℓ

    initial-inner  : InnerState         -- starting inner state
    initial-outer  : OuterState         -- starting outer state

    inner-step     : InnerState → Input → InnerState
    outer-step     : OuterState → InnerState → OuterState

open CascadedCoalgebra public

------------------------------------------------------------------------
-- Single-step cascade evolution.
--
-- Given current (inner, outer) joint state and an input, produce
-- the next (inner, outer) joint state.
--
-- This is the constructive composition: inner-step first (sees
-- only input), then outer-step (sees updated inner state). The
-- one-way coupling is enforced by the type signature.

step-cascade : (cc : CascadedCoalgebra {ℓ}) →
               (InnerState cc × OuterState cc) →
               Input cc →
               (InnerState cc × OuterState cc)
step-cascade cc (i , o) input =
  let i' = inner-step cc i input
      o' = outer-step cc o i'
  in (i' , o')

------------------------------------------------------------------------
-- Multi-step cascade evolution.
--
-- Fold step-cascade over a list of inputs.

run-cascade : (cc : CascadedCoalgebra {ℓ}) →
              List (Input cc) →
              (InnerState cc × OuterState cc)
run-cascade cc inputs =
  foldl (step-cascade cc) (initial-inner cc , initial-outer cc) inputs

------------------------------------------------------------------------
-- Constructive completeness witness.
--
-- The cascade's joint state after k inputs is deterministically
-- computable from the record's fields. Stated as the type signature
-- of run-cascade above; concrete proofs follow by structural induction
-- on the input list.

------------------------------------------------------------------------
-- The one-way-coupling property.
--
-- Inner-step depends only on (InnerState, Input); it does NOT take
-- OuterState. This is built into the type signature, so the property
-- is structural (not requiring a separate proof).
--
-- The substrate interpretation: the outer level (frequency-tracker
-- in PLL terms) cannot influence the inner level (phase-tracker).
-- The outer level only ADAPTS to what the inner level reports.

------------------------------------------------------------------------
-- Composition: 3-level (or n-level) cascade.
--
-- A 3-level cascade = (2-level cascade) + 1 outer layer that reads
-- the previous outer state. The composition is iterated:
--
--   cascade-cascade : CascadedCoalgebra at outer-2 + outer-3 →
--                     CascadedCoalgebra at (inner=⟨inner,outer-2⟩,
--                                            outer=outer-3)
--
-- Stated structurally; concrete n-level cascades instantiate
-- by stacking.

record TripleCascade : Set (lsuc ℓ) where
  field
    -- A 3-level cascade is a CascadedCoalgebra where InnerState
    -- itself contains a CascadedCoalgebra's joint state.
    layer-1-2  : CascadedCoalgebra {ℓ}
    Layer3     : Set ℓ
    initial-3  : Layer3
    step-3     : Layer3 →
                 (InnerState layer-1-2 × OuterState layer-1-2) →
                 Layer3

open TripleCascade public

------------------------------------------------------------------------
-- Categorical reading.
--
-- A CascadedCoalgebra is a sequential composition of two coalgebras
-- in the category Coalg(F) where F is a base functor. Per
-- [[coalgebraic-not-consumer-driven]]: each level is an unfolding
-- of gauge structure; the outer level unfolds atop the inner level's
-- already-unfolded structure.
--
-- Per [[3plus1-parity-universal]]: the (2 levels + 1 input-stream)
-- structure carries a 3+1 universal — 2 internal layers + 1 input
-- axis + 1 chirality (the one-way coupling direction).
--
-- Per [[homology-cohomology-recursion]]: the inner level is the
-- homology cycle (what the input stream reveals); the outer level
-- is the cohomology cocycle (what we infer FROM the homology). The
-- cascade closes one layer of the recursion at the dynamics level.
------------------------------------------------------------------------
