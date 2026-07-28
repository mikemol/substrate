------------------------------------------------------------------------
-- Substrate.Algebra.F2.HodgeDim4.ReservedBridge.SylowOrbitWitnesses
--
-- The three Sylow-canonical bridges as named orbit points of the
-- GaugeTorsor (= the GL(3, F₂)-torsor of Reserved↔SelfDual F₂-linear
-- bijections). Each is bridge-of of a multi-route arc Sylow generator
-- (per [[multi-route-equivariance-recovery]] +
-- [[klein-quartic-kinematic-anatomy]]):
--
--   * swap01-bridge   = bridge-of swap01-GL   (Sylow-2 witness)
--   * cycle3-bridge   = bridge-of cycle3-GL   (Sylow-3 witness)
--   * singer-bridge   = bridge-of singer-GL   (Sylow-7 witness)
--
-- Together with the canonical bridge (= bridge-of id-GL), these four
-- named bridges anchor the 168-element atlas at one element per
-- structurally distinct conjugacy-class layer of GL(3, F₂):
--
--   1. canonical              (identity)
--   2. swap01-bridge          (order-2 representative)
--   3. cycle3-bridge          (order-3 representative; = Alt-A from
--                              AlternativesAsOrbit)
--   4. singer-bridge          (order-7 representative)
--
-- Per [[universal-property-discipline]] + [[expose-generator-not-orbit]]:
-- these aren't separate bridge definitions — they're parametric
-- evaluations of bridge-of at named GL3F2 inputs. The structural
-- content lives in the GaugeTorsor + bridge-of from S3; this slice
-- merely names specific orbit points for downstream readability and
-- to make the connection to the Sylow-classification visible.
--
-- Per [[choice-rigidification]]: none of these bridges is "canonical"
-- — they're four named orbit points among the 168, chosen for their
-- Sylow-representative significance.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.F2.HodgeDim4.ReservedBridge.SylowOrbitWitnesses where

open import Substrate.Algebra.F2.Vector using (Vector)
open import Substrate.Algebra.F2.HodgeDim4.Bivector using (Bivector)
open import Substrate.Algebra.GL3F2.MultiRouteEquivariance.Cycle3GL using (cycle3-GL)
open import Substrate.Algebra.GL3F2.MultiRouteEquivariance.SingerGL using (singer-GL)
open import Substrate.Algebra.GL3F2.MultiRouteEquivariance.Swap01GL using (swap01-GL)
open import Substrate.Algebra.F2.HodgeDim4.ReservedBridge.GaugeTorsor
  using (bridge-of)

------------------------------------------------------------------------
-- 1. Sylow-2 bridge: swap01-bridge.
--
-- The Sylow-2 witness — corresponds to a basis transposition between
-- positions 0 and 1 of the F₂³ coordinate system. Anchors the
-- Sylow-2 (= flag-stabilizer) chart of the atlas.
------------------------------------------------------------------------

swap01-bridge : Vector 3 → Bivector
swap01-bridge = bridge-of swap01-GL

------------------------------------------------------------------------
-- 2. Sylow-3 bridge: cycle3-bridge.
--
-- The Sylow-3 witness — the 3-cycle on coordinate positions
-- 0 → 1 → 2 → 0. Anchors the Sylow-3 (= cyclic-coordinate-permutation)
-- chart of the atlas.
--
-- Identical to AlternativesAsOrbit.alt-A-orbit-bridge (up to module
-- reference); both reduce to bridge-of cycle3-GL. Named here for the
-- Sylow-3 classification, named there for the existing-alternative
-- identification.
------------------------------------------------------------------------

cycle3-bridge : Vector 3 → Bivector
cycle3-bridge = bridge-of cycle3-GL

------------------------------------------------------------------------
-- 3. Sylow-7 bridge: singer-bridge.
--
-- The Sylow-7 witness — the Singer cyclic on the Fano plane (= the
-- multiplication-by-x action in F₈ = F₂[x]/(x³+x+1) acting on F₂³).
-- Anchors the Sylow-7 (= Singer-cycle / projective-Fano) chart of
-- the atlas.
--
-- This is the FIRST bridge in the catalog that's NOT a basis
-- permutation — singer-Linear sends basis 2 to basis 0 +ⱽ basis 1
-- (a non-basis F₂ combination). Provides the substrate's first
-- explicit Sylow-7 witness for the gauge atlas at HodgeDim4.
------------------------------------------------------------------------

singer-bridge : Vector 3 → Bivector
singer-bridge = bridge-of singer-GL

------------------------------------------------------------------------
-- 4. Capstone.
--
-- After this slice, the atlas of 168 bridges has 4 named witnesses
-- (canonical + 3 Sylow representatives) anchoring the three Sylow-
-- subgroup chart layers of GL(3, F₂) per
-- [[klein-quartic-kinematic-anatomy]]. The remaining 164 bridges are
-- compositions of these four via GL(3, F₂)'s group structure (per
-- multi-route-equivariance: any subset containing prime-order
-- representatives generates the simple group of order 168 = 2³·3·7).
--
-- The full atlas catalogue (with explicit references to all named
-- witnesses) lands in S8 (AtlasCatalogue).
------------------------------------------------------------------------
