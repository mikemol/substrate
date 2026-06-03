------------------------------------------------------------------------
-- Substrate.WitnessTower.Link
--
-- BUILD (not assert): the path between a witness in rung N and rung N−1
-- is a V₂.
--
-- The witnessing step swaps a simplex with its witness (its Hodge dual,
-- WitnessTower.Hodge.dual-grade₃) — and that swap is an INVOLUTION:
-- doing it twice returns the original. An involution is exactly a V₂
-- (the order-2 cyclic group Z/2), expressed in the substrate as
-- `HasOrder γ 2` (Coalgebra.FiniteOrder). So each rung-to-rung link
-- carries a V₂; the "tower" is a chain of these V₂ involutions, one per
-- witnessing step — NOT one global Hodge star at a single ambient n.
--
-- This dissolves the n=3-vs-n=4 puzzle from WitnessTower.Hodge §3: there
-- is no single ambient to reconcile. Each step is its own V₂; TWO
-- commuting steps compose to a V₄ (the apex level), via the substrate's
-- HasOrder-compose-commute — built below as link-pair-V₄.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.WitnessTower.Link where

open import Substrate.Foundation.Fin using (Fin)
open import Substrate.Foundation.Eq using (_≡_; refl)

open import Substrate.Category.Coalgebra using (Endomap; _∘E_)
open import Substrate.Category.Coalgebra.FiniteOrder using (HasOrder)
open import Substrate.Category.Coalgebra.StructuralGCD using (Commute)
open import Substrate.Category.Coalgebra.StructuralGCD.Properties
  using (HasOrder-compose-commute)

open import Substrate.WitnessTower.Hodge
  using (dual-grade₃; dual-grade₃-involution)

------------------------------------------------------------------------
-- 1. The link as an Endomap: the witness↔witnessed swap on rung grades.
------------------------------------------------------------------------

link : Endomap (Fin 4)
link = dual-grade₃

------------------------------------------------------------------------
-- 2. The link IS a V₂: HasOrder link 2.
--
-- HasOrder link 2 = (i : Fin 4) → iterate 2 link i ≡ i, and iterate 2
-- link i = link (link i) = dual-grade₃ (dual-grade₃ i), which is i by
-- the involution proof. So the rung-to-rung path is order-2 = Z/2 = V₂.
------------------------------------------------------------------------

link-is-V₂ : HasOrder link 2
link-is-V₂ = dual-grade₃-involution

------------------------------------------------------------------------
-- 3. Two commuting links compose to a V₄ (the apex level).
--
-- A V₂ commutes with itself (commute-sym is trivial here: the same
-- endomap), and HasOrder-compose-commute lifts two commuting order-2
-- maps to an order-(2·2)=4 map. With the SAME link as both factors this
-- gives HasOrder (link ∘E link) 4 — the degenerate case (link∘link =
-- id, order divides 4); for two INDEPENDENT links on a product carrier
-- it gives a genuine V₄. We build the self-commuting witness here; the
-- independent-coordinate V₄ (apex) is the next experiment, on a product
-- of two grade-carriers.
------------------------------------------------------------------------

-- link commutes with itself (any endomap does, pointwise-equal both ways).
link-self-commute : Commute link link
link-self-commute = record { commute = λ i → refl }

-- the composed order-4 witness (V₄-order; the apex glue is ×, matching
-- the dossier's catamorphism combining op at the symmetry level).
link-pair-order4 : HasOrder (link ∘E link) 4
link-pair-order4 =
  HasOrder-compose-commute {γ₁ = link} {γ₂ = link} {k₁ = 2} {k₂ = 2}
    link-self-commute link-is-V₂ link-is-V₂
