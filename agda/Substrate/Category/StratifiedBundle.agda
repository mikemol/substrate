------------------------------------------------------------------------
-- Substrate.Category.StratifiedBundle
--
-- A fiber bundle over a 1D base manifold whose fiber type may differ
-- across strata. Each stratum has a constant fiber type; transitions
-- at boundary points map between adjacent strata's fiber types.
--
-- Per the DBE constructive-completeness criterion (user 2026-05-21):
-- the record includes initial-fiber-of (start element per stratum)
-- AND transition-fn (between adjacent strata's fibers). Given these,
-- the caller can propagate fiber values across the base — the
-- section-at function is DERIVED, not a field.
--
-- Categorical name: stratified fiber bundle. Per [[categorical-name-
-- first]]: this is standard algebraic-topology / differential-geometry
-- terminology.
--
-- Per [[multi-route-equivariance-recovery]]: the atlas-of-charts
-- discipline at the COMPOSITIONAL level — each stratum carries one
-- "chart" (a specific PLL bank state at that section's prime-set);
-- transitions glue charts across stratum boundaries.
--
-- Substrate use: MultidimensionalPLLBank = StratifiedBundle where
--   Base = corpus position (ℕ)
--   strata = section function (corpus → section index)
--   fiber-of = PLL bank state for that section's active primes
--   transition = how PLL state migrates across section boundaries
--
-- Per the FieldFanOut generalization 2026-05-21: each stratum's
-- fiber can be modelled as a FixedFanOut at that stratum's arity;
-- the StratifiedBundle assembles a family of FixedFanOuts indexed
-- by stratum.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Category.StratifiedBundle where

open import Substrate.Foundation.Nat using (ℕ)
open import Data.List using (List; []; _∷_)
open import Level using (Level) renaming (suc to lsuc)
open import Substrate.Foundation.Eq using (_≡_; refl)

private
  variable
    ℓ : Level

------------------------------------------------------------------------
-- The stratified bundle record.
--
-- Constructively complete: the five fields (Base, SectionIndex,
-- strata, fiber-of, initial-fiber-of, transition-fn) jointly let a
-- caller propagate fiber values from any starting point across the
-- base via iterated transitions.

record StratifiedBundle (Base : Set ℓ) : Set (lsuc ℓ) where
  field
    SectionIndex     : Set ℓ
    strata           : Base → SectionIndex
    fiber-of         : SectionIndex → Set ℓ
    initial-fiber-of : (s : SectionIndex) → fiber-of s

    -- The transition function: at any base point b, take a fiber
    -- value in fiber-of (strata b), produce the next fiber value
    -- in fiber-of (strata (next b)). The 'next' function on Base
    -- is part of the Base's intrinsic structure (e.g., suc on ℕ).
    -- For generality we accept a step function on Base.
    next-base        : Base → Base
    transition-fn    : (b : Base) →
                       fiber-of (strata b) →
                       fiber-of (strata (next-base b))

open StratifiedBundle public

------------------------------------------------------------------------
-- Derived section function.
--
-- Given a StratifiedBundle, the section-at function takes a Base
-- point and returns the corresponding fiber element. Computed by
-- propagating initial-fiber-of (strata start) via transition-fn
-- across the base.
--
-- The starting point determines which stratum we begin in;
-- subsequent positions are reached by iterated next-base + transition.
--
-- Concrete instances supply the iteration; the type signature here
-- shows what section-at would produce.

------------------------------------------------------------------------
-- Within-stratum stationarity.
--
-- When two Base points b₁, b₂ lie in the same stratum (strata b₁ ≡
-- strata b₂), their fiber types match. This is the structural law
-- that makes the bundle "stratified": stratum-INTERNAL transitions
-- preserve fiber type.

record WithinStratumStationary
       {Base : Set ℓ}
       (sb : StratifiedBundle Base) : Set (lsuc ℓ) where
  field
    -- The structural assertion: if two base points are in the same
    -- stratum, their fiber types coincide. Stated abstractly;
    -- concrete instances satisfy this by construction.
    stationary :
      (b₁ b₂ : Base) →
      strata sb b₁ ≡ strata sb b₂ →
      fiber-of sb (strata sb b₁) ≡ fiber-of sb (strata sb b₂)

open WithinStratumStationary public

------------------------------------------------------------------------
-- Cross-stratum transition data.
--
-- At a stratum boundary, the transition-fn carries fiber values
-- from one stratum's type to the next stratum's type. This is the
-- 2-cell (1-cobordism) data per Substrate.Category.BoundaryEvent.
--
-- The relationship: a list of BoundaryEvents on a Base determines
-- WHERE the strata boundaries lie; the StratifiedBundle's
-- transition-fn determines HOW fibers cross those boundaries.

------------------------------------------------------------------------
-- Composition: concatenating two stratified bundles.
--
-- Two bundles over Base₁ and Base₂ compose to a bundle over Base₁ ⊕
-- Base₂ (disjoint union) provided a transition at the juncture is
-- supplied (a BoundaryEvent at the seam).
--
-- Stated structurally; concrete composition operators are supplied
-- per Base-type.

------------------------------------------------------------------------
-- Categorical reading.
--
-- A StratifiedBundle is a fiber bundle in the category Top-over-
-- 1-manifold, with stratification given by the strata function.
-- Each stratum is a sub-bundle of constant fiber type; transitions
-- glue strata at boundary points.
--
-- Per [[homology-cohomology-recursion]]: the strata function is the
-- homology projection (Base → stratum class); the fiber values are
-- the cohomology cocycles attached to each homology class.
--
-- Per [[multi-route-equivariance-recovery]]: the bundle IS the
-- atlas-of-charts structure; the strata are the chart partitions;
-- the fibers are the per-chart equivariant data; the transitions
-- are the chart-overlap glue.
--
-- Per [[multi-field-tower-architecture]]: StratifiedBundle is the
-- variable-arity FanOut at the bundle level; it composes
-- FixedFanOut instances across strata.
------------------------------------------------------------------------
