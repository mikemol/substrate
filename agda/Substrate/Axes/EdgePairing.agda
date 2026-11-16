------------------------------------------------------------------------
-- Substrate.Axes.EdgePairing
--
-- Defines: edge-v₄
-- ⟡cap-128-forcing: one lemma, one elaboration unit.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Axes.EdgePairing where

open import Substrate.Groups.V4.Bijection.V4 using (V₄)
open import Substrate.Groups.V4.Operations using (_·₄_)
open import Substrate.Axes.Axis using (Axis)
open import Substrate.Axes.VOfAxis using (v-of-axis)


------------------------------------------------------------------------
-- `edge-v₄ s t` — the V₄ element of the matching that pairs s with t.
--
-- ⚑ THE DIAGONALIZATION, NOT A CONSTRAINT (user, 2026-08-07: *"that's the
-- diagonalization, and is already in-hand as the tower grows"*). Choosing an
-- EDGE {s,t} out of four cells FORCES the complementary pair — there is no
-- second choice to make, because 4 = 2 + 2. So the matching is PRODUCED by
-- the ascent rather than consulted from below, and `w-opposite` is not a
-- fourth negation to supply but a statement about which block the witness
-- falls in.
--
-- ⚑ AND `Pairing` ALREADY EXISTS, PROVED BIJECTIVE TO V₄∖{e}.
-- `Cocycles.V4Signature.Pairing.Type` declares exactly the three matchings
-- (`α-pair = {D,C}|{S,W}` etc. — the same partitions as
-- `scratch/meta_protocol.py:29`'s `PAIRINGS`, written independently), and
-- `Pairing.Structural.Pairing↔V4-Nonzero` proves the bijection with both
-- round-trips. This module supplies the missing ARROW INTO that: an edge
-- determines its V₄ element.
--
-- ⚑ NON-IDENTITY EXACTLY WHEN THE EDGE IS REAL. `v ·₄ v = e` in V₄, so
-- `edge-v₄ a a ≡ e` — the degenerate "edge" from a point to itself yields the
-- identity, which names no matching. That is why `V₄→Pairing` demands a
-- `≢ e` witness: the proof that s and t are distinct is what licenses reading
-- a matching off the edge, and the two facts are the same fact.
--
-- ⚑ MEASURED, TWO WAYS, THAT V₄ BELONGS TO THE TOWER — the directionality
-- question, and the answer is BOTH:
--   * `WitnessTower.FirstAppearance` — the (2,2) class is ABSENT at rung 3
--     and equals 3 at rung 4 (`census-moved4-3-absent`,
--     `census-moved4-4-debut`). A double-transposition needs four points, so
--     the tower's ascent BRINGS V₄ INTO BEING at a definite rung.
--   * `WitnessTower.WholeTower` — `S₄ = V₄ ⋊ (Z₃ ⋊ Z₂)`, apex/triangle/edge.
--     V₄ is the normal factor of the top rung, and quotienting by it DROPS a
--     rung (`stab-step : Stab≃S₃ anchor`).
-- The census says WHEN V₄ becomes constructible; the decomposition says WHAT
-- it does once it exists. Neither module cites the other — the identification
-- of FirstAppearance's `3` with WholeTower's `V₄∖{e}` is header prose, not a
-- term.
------------------------------------------------------------------------

edge-v₄ : Axis → Axis → V₄
edge-v₄ s t = v-of-axis s ·₄ v-of-axis t
