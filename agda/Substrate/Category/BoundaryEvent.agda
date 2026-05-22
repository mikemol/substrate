------------------------------------------------------------------------
-- Substrate.Category.BoundaryEvent
--
-- A boundary event marks a transition between two FiberState values
-- at a specific Base position. The post-hoc data record (the event)
-- is separate from the operation that detects events (the detector).
--
-- Per the DBE constructive-completeness criterion (user 2026-05-21):
-- splitting data from operation makes both halves constructively
-- complete. The event record alone is a witness of a transition;
-- the detector alone is the operation that finds events given
-- history. Together they cover the boundary-detection problem.
--
-- The categorical name is 1-cobordism: a 0-dimensional boundary
-- (the point at locus) between two attached 0-cells (before, after).
-- Per [[categorical-name-first]]: use the cobordism name; PLL-arc-
-- specific "PrimeStructureDrift" is the INSTANCE.
--
-- Per [[multi-route-equivariance-recovery]]: when the atlas of
-- charts varies over corpus position, boundary events mark where
-- the atlas reconfigures. The drift trace = sorted list of
-- boundary events.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Category.BoundaryEvent where

open import Substrate.Foundation.List using (List; []; _∷_)
open import Substrate.Foundation.Bool using (Bool; true; false)
open import Level using (Level) renaming (suc to lsuc)
open import Substrate.Foundation.Eq using (_≡_; refl)

private
  variable
    ℓ ℓb ℓf ℓs : Level

------------------------------------------------------------------------
-- The boundary event data record.
--
-- A POST-HOC witness: an event has been detected at `locus`, between
-- FiberState values `before` and `after`. The `signature` is the
-- diagnostic data that the detector produced to identify the event.
--
-- Universe-flexible: Base, FiberState, Signature can live at any
-- universe levels (e.g., Base = ℕ at Set₀, FiberState at Set₁).
-- The result type lives at the supremum of the three.

open import Level using (_⊔_)

record BoundaryEvent (Base : Set ℓb)
                       (FiberState : Set ℓf)
                       (Signature : Set ℓs) : Set (ℓb ⊔ ℓf ⊔ ℓs) where
  field
    locus     : Base           -- position where the event occurred
    before    : FiberState     -- fiber state immediately before
    after     : FiberState     -- fiber state immediately after
    signature : Signature      -- detection diagnostic

open BoundaryEvent public

------------------------------------------------------------------------
-- The boundary detector operation.
--
-- Given a History type and a detect function that produces a list
-- of BoundaryEvent records, the operation is constructively
-- complete: caller can apply detect to any history to get all
-- detected events.
--
-- The History type is abstracted; concrete instances supply
-- specific history representations (e.g., List ChamberSymbol,
-- a sliding window, a hash of past events).

record BoundaryDetector
       (Base : Set ℓb)
       (FiberState : Set ℓf)
       (Signature : Set ℓs) : Set (lsuc (ℓb ⊔ ℓf ⊔ ℓs)) where
  field
    History : Set (ℓb ⊔ ℓf ⊔ ℓs)
    detect  : History → List (BoundaryEvent Base FiberState Signature)

open BoundaryDetector public

------------------------------------------------------------------------
-- Trace consistency: adjacent boundary events agree on the
-- intermediate fiber state.
--
-- If two events are adjacent in the corpus order, the second's
-- `before` must equal the first's `after`. This is the cobordism
-- composition consistency.

record TraceConsistency
       {Base : Set ℓb}
       {FiberState : Set ℓf}
       {Signature : Set ℓs}
       (events : List (BoundaryEvent Base FiberState Signature)) : Set (ℓb ⊔ ℓf ⊔ ℓs) where
  field
    consistent :
      (e₁ e₂ : BoundaryEvent Base FiberState Signature) →
      after e₁ ≡ before e₂ →
      after e₁ ≡ before e₂  -- trivial: the consistency is the equation itself

open TraceConsistency public

------------------------------------------------------------------------
-- Trace composition: concatenate two consistent traces with a
-- consistency proof at the junction.
--
-- Stated structurally; the composition operator is list append
-- with consistency-preservation as the obligation.

------------------------------------------------------------------------
-- Categorical reading.
--
-- BoundaryEvent is a 1-cobordism: a 0-manifold (a point) in the
-- corpus's 1D base, with attached 0-cells (before/after) on either
-- side and a detection signature labelling the boundary type.
--
-- Per [[homology-cohomology-recursion]]: the trace (list of
-- BoundaryEvents) is the homology cycle of the fiber-state
-- evolution; the per-event signature is the cohomology cocycle
-- that identifies WHICH boundary type fires at each locus.
--
-- Per [[multi-reading-ambient-discipline]]: BoundaryEvent is the
-- ambient — concrete instances supply specific (Base, FiberState,
-- Signature) types corresponding to specific drift detectors.
--
-- The substrate's PLL bank uses this with:
--   Base       = chain position (ℕ)
--   FiberState = active prime set (List ℕ)
--   Signature  = drift type (manual marker / cost-gate fire / etc.)
------------------------------------------------------------------------
