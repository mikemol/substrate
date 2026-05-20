------------------------------------------------------------------------
-- Substrate.Algebra.F2.HodgeDim4.Cone-HodgeStar-EdgeApex
--
-- Hodge ★ as an edge-apex of a Cone over Bivector-derived readings.
--
-- Per [[project-3plus1-is-cone-instance]] apex-can-be-edge: a Cone's
-- apex can be a morphism (object in the arrow category). Hodge ★ at
-- dim 4 IS such a morphism: ★ : Bivector → Bivector (an involution).
-- As an apex-edge, ★ provides the structural witness binding
-- Bivector-readings together.
--
-- For the Cone's base, we pick a TRIVIAL reading (constant projection
-- to Fin 1) — this demonstrates the edge-apex shape without needing
-- to verify a non-trivial reading's ★-invariance. A more substantive
-- instance would use a ★-invariant function like weight-parity (from
-- Bivector-F2Graded, slice 18 of the previous arc).
--
-- The instance lands as type-correct; the proof obligations for
-- non-trivial readings are deferred follow-ons.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.F2.HodgeDim4.Cone-HodgeStar-EdgeApex where

open import Data.Fin using (Fin; zero)
open import Relation.Binary.PropositionalEquality using (_≡_; refl)

open import Substrate.Algebra.F2.Vector using (Vector)
open import Substrate.Algebra.F2.Linear using (apply)
open import Substrate.Algebra.F2.HodgeDim4.Bivector using (Bivector)
open import Substrate.Algebra.F2.HodgeDim4.HodgeStar using (hodge-star)
open import Substrate.Category.Cone.EdgeApex

------------------------------------------------------------------------
-- N-1: The Bivector → Bivector edge from Hodge ★.
------------------------------------------------------------------------

hodge-edge : Bivector → Bivector
hodge-edge = apply hodge-star

------------------------------------------------------------------------
-- N-2: Trivial-base EdgeApexCone instance.
--
-- One reading, mapping any Bivector to Fin 1's zero (constant
-- projection). Commutativity is trivial (refl) since both legs are
-- constant.
------------------------------------------------------------------------

Base-Trivial : Fin 1 → Set
Base-Trivial _ = Fin 1

leg-trivial : (i : Fin 1) → Bivector → Fin 1
leg-trivial _ _ = zero

HodgeStar-EdgeApex-Cone :
  EdgeApexCone 1 Base-Trivial Bivector Bivector hodge-edge
HodgeStar-EdgeApex-Cone = record
  { leg-src = leg-trivial
  ; leg-tgt = leg-trivial
  ; commute = λ _ _ → refl
  }

------------------------------------------------------------------------
-- N-3: Capstone.
--
-- After this slice: Hodge ★ instantiates the EdgeApexCone primitive
-- with a trivial reading. The TYPE-level demonstration is complete:
-- the apex can be a morphism, and the cone's structure accommodates
-- the morphism's two endpoints with a commutativity witness.
--
-- The TRIVIAL reading (constant Fin 1 projection) is structurally
-- minimal; it shows the cone shape applies but doesn't exercise the
-- commutativity meaningfully. For a substantive instance, replace
-- the trivial reading with a ★-invariant function (weight-parity,
-- self-dual indicator, etc.), with the commutativity proved via
-- ★'s invariance properties.
--
-- Substrate-wide consequence: ANY substrate morphism (Hodge ★,
-- congruence-act, basis-permutation-Linear's apply, etc.) can serve
-- as an apex-edge for a Cone over appropriate readings.
--
-- Per [[project-3plus1-is-cone-instance]]: the apex-edge realization
-- is the substrate's structural answer to "the +1 witness can be a
-- morphism, not just an element." Hodge ★ is the canonical example.
--
-- Deferred follow-ons:
--
--   * **★-invariant readings**: replace trivial reading with
--     weight-parity (Bivector-F2Graded); requires ★-preserves-
--     weight-parity lemma.
--
--   * **Self-dual subspace as base**: the 3-dim self-dual subspace
--     of Bivector gives a 3-reading base with ★ as apex-edge; this
--     is the (3, edge)-cone realization of the dim-4 Hodge structure.
--
--   * **Higher-cell apex** (apex as apex-edge in Arr(Arr(C))):
--     two-step morphism apex; e.g., a natural transformation between
--     two ★-like operations.
------------------------------------------------------------------------
