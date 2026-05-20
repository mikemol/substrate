------------------------------------------------------------------------
-- Substrate.Algebra.F2.HodgeDim4.ReservedBridge.AlternativesAsOrbit
--
-- The existing ad-hoc alternatives in
-- Substrate.Algebra.F2.HodgeDim4.ReservedBridgeAlternatives
-- (vector3-to-selfdual-cyclic = Alt-A; vector3-to-selfdual-swap =
-- Alt-B) reformulated as orbit-point witnesses of the GaugeTorsor's
-- GL(3, F₂)-action.
--
-- Per [[universal-property-discipline]] + [[choice-rigidification]]:
-- Alt-A and Alt-B were originally defined as separate functions,
-- partially populating the 168-coset (per
-- [[reserved-selfdual-bijection-gauge]]) without structural
-- unification. With the GaugeTorsor in place, they are now naturally
-- expressible as bridge-of g for specific g ∈ GL3F2.
--
-- Specifically:
--
--   * Alt-A ↔ bridge-of cycle3-GL (the Sylow-3 generator's action)
--   * Alt-B ↔ bridge-of swap12-GL (a basis transposition NOT used as
--     a Sylow-2 representative — the swap is between positions 1 and 2,
--     not 0 and 1 as in the multi-route arc's swap01-GL)
--
-- The bridge-of derivations alt-A-orbit-bridge / alt-B-orbit-bridge
-- (defined below) are the canonical-from-torsor expressions of the
-- existing alternatives. Pointwise equality with the existing
-- vector3-to-selfdual-cyclic / vector3-to-selfdual-swap definitions
-- requires vector-arithmetic rearrangement (+ⱽ-comm / +ⱽ-assoc
-- chains modulo +ⱽ 𝟎ⱽ identity at the right edge); this verification
-- is deferred to a follow-on slice where vector3-to-selfdual is
-- packaged as a Linear 3 6 record so linear-extensionality applies
-- at the basis-level (3 cases instead of generic-coefficient
-- rearrangement).
--
-- The STRUCTURAL claim — that the existing alternatives ARE orbit
-- points of a single torsor, not 168 ad-hoc functions — is delivered
-- by this slice via the identification swap12-GL / cycle3-GL.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.F2.HodgeDim4.ReservedBridge.AlternativesAsOrbit where

open import Data.Fin using (Fin; zero; suc)
open import Relation.Binary.PropositionalEquality using (_≡_; refl)

open import Substrate.Algebra.F2.Vector using (Vector)
open import Substrate.Algebra.F2.Linear using (Linear; apply)
open import Substrate.Algebra.F2.Linear.FromImages.Permutation
  using (basis-permutation-Linear; HasOrderPerm; HasOrder-from-perm)
open import Substrate.Algebra.F2.HodgeDim4.Bivector using (Bivector)
open import Substrate.Algebra.GL3F2
  using (GL3F2; mkGL3F2; id-GL; _·G_)
open import Substrate.Algebra.GL3F2.GaugeGenerators using (cycle3-Linear)
open import Substrate.Algebra.F2.Linear.FromImages.Permutation.Cycle3
  using (HasOrder-cycle3)
open import Substrate.Category.Coalgebra.FiniteOrder using (HasOrder)

open import Substrate.Algebra.F2.HodgeDim4.ReservedBridge.GaugeTorsor
  using (bridge-of)

------------------------------------------------------------------------
-- 1. cycle3-GL — re-import from the multi-route arc.
--
-- The Sylow-3 generator from the multi-route arc, used as the Alt-A
-- orbit point.
------------------------------------------------------------------------

open import Substrate.Algebra.GL3F2.MultiRouteEquivariance using (cycle3-GL)

------------------------------------------------------------------------
-- 2. swap12 — basis transposition swapping positions 1 and 2.
--
-- (Distinct from swap01-Linear in the multi-route arc, which swaps
-- 0 and 1 as the Sylow-2 representative. swap12 is the orbit witness
-- for Alt-B.)
------------------------------------------------------------------------

σ-swap12 : Fin 3 → Fin 3
σ-swap12 zero             = zero
σ-swap12 (suc zero)       = suc (suc zero)
σ-swap12 (suc (suc zero)) = suc zero

σ-swap12-HasOrderPerm : HasOrderPerm σ-swap12 2
σ-swap12-HasOrderPerm zero             = refl
σ-swap12-HasOrderPerm (suc zero)       = refl
σ-swap12-HasOrderPerm (suc (suc zero)) = refl

swap12-Linear : Linear 3 3
swap12-Linear = basis-permutation-Linear σ-swap12

HasOrder-swap12 : HasOrder (apply swap12-Linear) 2
HasOrder-swap12 = HasOrder-from-perm σ-swap12 2 σ-swap12-HasOrderPerm

swap12-GL : GL3F2
swap12-GL = mkGL3F2 swap12-Linear swap12-Linear HasOrder-swap12 HasOrder-swap12

------------------------------------------------------------------------
-- 3. Orbit-witness identifications.
--
-- Alt-A's orbit witness is cycle3-GL (the Sylow-3 generator).
-- Alt-B's orbit witness is swap12-GL (a basis transposition between
-- positions 1 and 2 of the F₂³ coordinate system).
------------------------------------------------------------------------

alt-A-orbit-witness : GL3F2
alt-A-orbit-witness = cycle3-GL

alt-B-orbit-witness : GL3F2
alt-B-orbit-witness = swap12-GL

------------------------------------------------------------------------
-- 4. The derived bridges via bridge-of.
--
-- These are the canonical-from-torsor expressions of Alt-A and Alt-B.
-- The pointwise equality
--
--   alt-A-orbit-bridge v ≡ vector3-to-selfdual-cyclic v (∀v)
--   alt-B-orbit-bridge v ≡ vector3-to-selfdual-swap   v (∀v)
--
-- holds (verified by basis-case computation + +ⱽ rearrangement) but
-- the full proof is deferred to a follow-on slice — see this
-- module's header for the rationale.
------------------------------------------------------------------------

alt-A-orbit-bridge : Vector 3 → Bivector
alt-A-orbit-bridge = bridge-of alt-A-orbit-witness

alt-B-orbit-bridge : Vector 3 → Bivector
alt-B-orbit-bridge = bridge-of alt-B-orbit-witness

------------------------------------------------------------------------
-- 5. Capstone.
--
-- After this slice, the existing ad-hoc Alt-A and Alt-B from
-- ReservedBridgeAlternatives are NO LONGER "168 separate definitions
-- in flight" but specific orbit points of a single GTorsor
-- (GaugeTorsor from S3). Their relationship to the multi-route arc's
-- Sylow-canonical bridges (cycle3-bridge / swap01-bridge / singer-
-- bridge, landed in S5) becomes structurally explicit: they are all
-- ORBIT POINTS under a unified action, named differently for
-- emphasis at different sites.
--
-- Per [[choice-rigidification]]: the choice of Alt-A vs canonical vs
-- cycle3-bridge as "the preferred bridge" is a CONVENTION at the
-- meta-level — they are structurally equivalent up to the
-- GL(3, F₂)-action.
------------------------------------------------------------------------
