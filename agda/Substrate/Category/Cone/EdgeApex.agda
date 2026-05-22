------------------------------------------------------------------------
-- Substrate.Category.Cone.EdgeApex
--
-- Cone with apex an EDGE (a morphism in the underlying category,
-- viewed as an object in the arrow category Arr(C)).
--
-- Per the user's structural framing: the apex of an M:N cone doesn't
-- have to be a single object — it can be a morphism between two
-- objects, which IS an object in the arrow category. "Object or
-- morphism, same id has both perspectives."
--
-- For Set-level cones, an EdgeApex is:
--   * src, tgt : Set (the two endpoint objects of the edge).
--   * mor : src → tgt (the edge itself).
--   * For each base i: a leg from src to Base i AND a leg from tgt
--     to Base i, commuting with mor (i.e., the square (src → tgt) →
--     (Base i, Base i) commutes via the leg).
--
-- The commutativity ensures the edge-apex provides COHERENT
-- projection — both endpoints of the edge agree on how they map to
-- each base reading.
--
-- Per [[project-3plus1-is-cone-instance]]: the apex-as-edge enables
-- richer M:N cones where the witness is a morphism (e.g., Hodge ★
-- as an apex-edge in the Bivector ↔ Bivector arrow category).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Category.Cone.EdgeApex where

open import Substrate.Foundation.Fin using (Fin)
open import Substrate.Foundation.Nat using (ℕ)
open import Substrate.Foundation.Level using (Level; _⊔_)
open import Substrate.Foundation.Eq using (_≡_)

private
  variable
    ℓ : Level

------------------------------------------------------------------------
-- The EdgeApexCone record.
------------------------------------------------------------------------

record EdgeApexCone
  (n : ℕ) (Base : Fin n → Set ℓ)
  (src tgt : Set ℓ) (mor : src → tgt) : Set ℓ where
  field
    leg-src : (i : Fin n) → src → Base i
    leg-tgt : (i : Fin n) → tgt → Base i
    commute : (i : Fin n) (s : src) →
              leg-tgt i (mor s) ≡ leg-src i s

------------------------------------------------------------------------
-- Capstone.
--
-- After this slice: cones can have apex-as-edge in addition to the
-- single-object apex from Substrate.Category.Cone (slice 1 of this
-- arc). The commutativity condition `leg-tgt ∘ mor = leg-src` makes
-- the edge-apex a COHERENT witness — both endpoints project to base
-- consistently.
--
-- Substrate use: an apex-edge cone realizes "the witness is itself
-- a morphism" — e.g., Hodge ★ at the Bivector level is a morphism
-- Bivector → Bivector (an involution); viewed as an edge-apex over
-- the Bivector readings, it's a (M, edge)-cone.
--
-- Per [[project-3plus1-is-cone-instance]] apex-can-be-edge: this
-- primitive realizes that generality. Future slices can extend
-- to apex = arrow-of-arrows (2-cell) and beyond.
--
-- Deferred follow-ons:
--
--   * **Apex as 2-cell**: apex in Arr(Arr(C)). The recursive
--     "morphism-or-object same id" perspective applied twice.
--
--   * **Compose two edge-apex cones**: when the apex-edges are
--     composable (target of one = source of another), the cones
--     compose to a longer-edge-apex cone.
------------------------------------------------------------------------
