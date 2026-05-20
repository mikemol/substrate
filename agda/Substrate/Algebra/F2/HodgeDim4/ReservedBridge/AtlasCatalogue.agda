------------------------------------------------------------------------
-- Substrate.Algebra.F2.HodgeDim4.ReservedBridge.AtlasCatalogue
--
-- The full atlas of Reserved↔SelfDual F₂-linear bijections (= 168
-- bridges, per [[reserved-selfdual-bijection-gauge]]) catalogued as
-- named orbit points of the GaugeTorsor.
--
-- This module is the re-export hub for the universal-property
-- unification arc (S1-S7). After S8, downstream consumers have a
-- SINGLE IMPORT POINT for the full bridge catalogue, with named
-- representatives for each structurally distinct conjugacy-class
-- layer of GL(3, F₂).
--
-- The atlas is organized by Sylow-classification per
-- [[klein-quartic-kinematic-anatomy]]:
--
--   1. Identity layer:
--      * canonical-bridge = bridge-of id-GL
--        (the basepoint of the torsor; convention not privilege)
--
--   2. Sylow-2 layer (order-2 representatives):
--      * swap01-bridge = bridge-of swap01-GL
--        (basis transposition 0 ↔ 1; multi-route arc's Sylow-2)
--      * alt-B-orbit-bridge = bridge-of swap12-GL
--        (basis transposition 1 ↔ 2; matches existing Alt-B)
--
--   3. Sylow-3 layer (order-3 representative):
--      * cycle3-bridge = bridge-of cycle3-GL
--      * alt-A-orbit-bridge = bridge-of cycle3-GL
--        (same; named twice for Sylow-classification vs.
--         existing-alternative emphasis)
--
--   4. Sylow-7 layer (order-7 representative):
--      * singer-bridge = bridge-of singer-GL
--        (Singer cycle on the Fano plane; the first non-basis-
--         permutation bridge in the catalog)
--
--   5. Hodge-★-trivial layer:
--      * star-act (bridge-of g) ≡ bridge-of g (∀ g)
--        — Hodge ★ acts trivially on the torsor; corresponds to id-GL.
--
-- All 168 bridges are reachable from any orbit point via the
-- GL(3, F₂)-action (per S3 GaugeTorsor's gauge-transitive). The 4
-- named representatives above + the gauge action together
-- exhaustively describe the atlas.
--
-- Per [[universal-property-discipline]] + [[choice-rigidification]]:
-- this is NOT "the 168 bridges enumerated as 168 separate objects."
-- It's "4 named orbit points + the torsor action." The remaining 164
-- bridges are accessible programmatically as bridge-of g for
-- g ∈ GL3F2 — no separate definitions needed.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.F2.HodgeDim4.ReservedBridge.AtlasCatalogue where

------------------------------------------------------------------------
-- 1. Re-export the named bridges from S3-S5.
------------------------------------------------------------------------

-- Identity layer (canonical bridge).
open import Substrate.Algebra.F2.HodgeDim4.ReservedBridge.GaugeTorsor
  using (bridge-of; GaugeTorsor; bridge-of-id;
         gauge-act; gauge-act-id; gauge-act-·G;
         gauge-transitive; gauge-free) public

-- Existing-alternatives layer (Alt-A, Alt-B as orbit points).
open import Substrate.Algebra.F2.HodgeDim4.ReservedBridge.AlternativesAsOrbit
  using (alt-A-orbit-witness; alt-A-orbit-bridge;
         alt-B-orbit-witness; alt-B-orbit-bridge;
         swap12-Linear; swap12-GL) public

-- Sylow-canonical layer (3 Sylow witnesses).
open import Substrate.Algebra.F2.HodgeDim4.ReservedBridge.SylowOrbitWitnesses
  using (swap01-bridge; cycle3-bridge; singer-bridge) public

-- Hodge-★-trivial layer (★-action on the torsor).
open import Substrate.Algebra.F2.HodgeDim4.HodgeStar.AsGaugeAction
  using (star-act; bridge-lands-in-SelfDual;
         hodge-trivial-on-bridge; hodge-as-id-GL) public

-- Underlying GL3F2 generators for completeness.
open import Substrate.Algebra.GL3F2.MultiRouteEquivariance
  using (swap01-GL; cycle3-GL; singer-GL) public

------------------------------------------------------------------------
-- 2. Capstone — the atlas in one place.
--
-- The universal-property unification arc (S1-S8 in this arc, S1-S5 in
-- the prior multi-route equivariance arc) closes the original gauge
-- question from [[reserved-selfdual-bijection-gauge]]:
--
--   The "168 ad-hoc bijections" become 4 named orbit points + a
--   single torsor structure (GaugeTorsor over GL(3, F₂)).
--
-- The named representatives organize by:
--
--   * Identity:    canonical-bridge       (id-GL)
--   * Sylow-2:     swap01-bridge          (basis 0↔1 transposition)
--                  alt-B-orbit-bridge     (basis 1↔2 transposition)
--   * Sylow-3:     cycle3-bridge          (= alt-A-orbit-bridge)
--   * Sylow-7:     singer-bridge          (Singer cycle on F₂³)
--   * ★-trivial:   any bridge under star-act stays put
--
-- By [[multi-route-equivariance-recovery]]: the orbit of these
-- generators under GL(3, F₂)-multiplication covers the full 168
-- bridges. No bridge is "more canonical" than any other — they're
-- structurally equivalent up to the chosen basepoint convention.
--
-- This closes the arc's deliverable: the gauge-freedom space at
-- HodgeDim4 is now a SINGLE OBJECT (the GaugeTorsor), not 168 ad-hoc
-- alternatives.
------------------------------------------------------------------------
