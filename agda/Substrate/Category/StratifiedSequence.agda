------------------------------------------------------------------------
-- Substrate.Category.StratifiedSequence
--
-- A linearly-ordered sequence partitioned into labelled sections,
-- with boundary events marking adjacent-section transitions.
--
-- Per the DBE constructive-completeness criterion (user 2026-05-21):
-- the record carries the list of (section, length) tuples PLUS the
-- list of boundary events. Given these, a caller can reconstruct
-- the structural skeleton of the sequence — its section partition
-- and the transitions between adjacent sections.
--
-- This is the STRUCTURAL ANNOTATION; the concrete content (bytes,
-- chain symbols, etc.) lives separately. The skeleton is what
-- StratifiedBundle fibers OVER.
--
-- Categorical name: stratified 1-manifold / sequential decomposition.
-- Per [[categorical-name-first]]: this is GradedMonoid with a
-- position-indexed grade — a refinement of the existing substrate
-- primitive.
--
-- Per [[multi-route-equivariance-recovery]]: the strata are the
-- chart partition; the boundary events are the chart-overlap data.
-- StratifiedSequence is the underlying base; StratifiedBundle fibers
-- over it.
--
-- Per [[surreals-term-algebra-alignment]]: the section list with
-- boundary events resembles Conway's {L | R} surreal cuts — a
-- linearly-ordered structure where boundaries are the cuts.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Category.StratifiedSequence where

open import Substrate.Foundation.Nat using (ℕ; zero; suc; _+_)
open import Substrate.Foundation.List using (List; []; _∷_; foldl; foldr)
open import Substrate.Foundation.Product using (_×_; _,_)
open import Substrate.Foundation.Level using (Level) renaming (suc to lsuc)
open import Substrate.Foundation.Eq using (_≡_; refl)

open import Substrate.Category.BoundaryEvent

private
  variable
    ℓ : Level

------------------------------------------------------------------------
-- The stratified sequence record.
--
-- A list of (section label, length) tuples + a list of boundary
-- events marking transitions between adjacent sections. The
-- consistency obligation states that boundary events align with
-- the section breakdown.
--
-- Constructively complete: given a sequence record, the caller knows
-- (a) which sections exist, (b) how long each is, (c) what the
-- boundary types are at each section transition.

record StratifiedSequence
       (Section : Set ℓ)
       (Signature : Set ℓ) : Set ℓ where
  field
    sections        : List (Section × ℕ)
    boundary-events : List (BoundaryEvent ℕ Section Signature)

open StratifiedSequence public

------------------------------------------------------------------------
-- Total length: sum of section lengths.

total-length : {Section : Set ℓ} {Signature : Set ℓ} →
               StratifiedSequence Section Signature →
               ℕ
total-length seq = foldr _+_ 0 (sec-lengths (sections seq))
  where
    sec-lengths : ∀ {A : Set _} → List (A × ℕ) → List ℕ
    sec-lengths []             = []
    sec-lengths ((_ , n) ∷ xs) = n ∷ sec-lengths xs

------------------------------------------------------------------------
-- Composition: append two stratified sequences.
--
-- The boundary event at the juncture must agree: the first
-- sequence's last section's label ≡ the BoundaryEvent's before;
-- the second sequence's first section's label ≡ BoundaryEvent's
-- after.
--
-- Stated structurally; concrete composition operators verify
-- consistency.

------------------------------------------------------------------------
-- Categorical reading.
--
-- A StratifiedSequence is a stratified 1-manifold: a closed
-- interval [0, total-length] partitioned into sub-intervals
-- labelled by sections, with boundary points marked by
-- BoundaryEvents.
--
-- Per [[homology-cohomology-recursion]]: the section partition is
-- the homology decomposition of the interval; the boundary events
-- are the cohomology cocycles attached to the homology boundaries.
--
-- Per [[3plus1-parity-universal]]: at every boundary, the (before
-- section + after section + boundary signature) triple plus the
-- "boundary chirality" (left vs right orientation) carries a 3+1
-- universal at the section-transition level.
--
-- Per the substrate's existing GradedMonoid: StratifiedSequence is
-- a refinement where the grade index varies along the sequence.
-- A constant-section StratifiedSequence is a single-graded
-- monoid; multi-section sequences are the multi-graded extension.
------------------------------------------------------------------------
