------------------------------------------------------------------------
-- Substrate.Groups.V4.IsHomomorphism
--
-- The predicate "f : V₄ → V₄ preserves the V₄ group multiplication."
--
-- This predicate was inlined as the GOAL TYPE across every Hom file
-- in Substrate.Groups.Actions.S3-on-V4.Hom{Rotations,Swaps} — five
-- files, each with the same `∀ v₁ v₂ → f (v₁ · v₂) ≡ f v₁ · f v₂`
-- shape, varying only in which specific `f = act-on-canonical N H`
-- the goal targets.
--
-- Per [[project-cluster-to-action-analysis-2026-05]] and the user's
-- SPPF (shared-packed-parse-forest) framing: the goal shape itself
-- IS a shared parse sub-tree across all Hom files. Naming it as
-- `IsHomomorphism` makes the sub-tree a single named node;
-- the per-file (N, H) deltas become the case-content while the
-- predicate shape is shared.
--
-- This is just `f preserves V₄'s _·_` — the canonical "is a
-- homomorphism" predicate restricted to endomaps of V₄.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Groups.V4.IsHomomorphism where
open import Substrate.Groups.V4.Operations using (_·_)

import Substrate.Groups.V4.Operations as V4
open import Substrate.Groups.V4.Bijection using (V₄)
open import Substrate.Foundation.Eq using (_≡_)

IsHomomorphism : (V₄ → V₄) → Set
IsHomomorphism f = ∀ v₁ v₂ → f (v₁ · v₂) ≡ f v₁ · f v₂
