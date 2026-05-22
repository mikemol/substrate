------------------------------------------------------------------------
-- Substrate.Category.AtlasOfProbes
--
-- II-arc: atlas-of-probes structure inspired by the kinematic
-- gauge-sacrifice catalog (Thompson, Rzeppa, Weiss, etc.). Per
-- [[multi-route-equivariance-recovery]]: equivariance is a
-- joint-structural property of the atlas of charts, not a
-- per-chart property. Each probe is one chart looking at the
-- chain walk's state at a specific past offset; the atlas of
-- probes jointly carries predictive information.
--
-- Per [[kinematic-gauge-sacrifice-catalog]]: the 16+ CV-joint
-- family members map to atlases at three Sylow targets:
--   Sylow-2 (F₂³): Thompson, Cardan, Cornay, Rag, Clemens
--   Sylow-3 (F₃ → S¹): Rzeppa, Tripod, DOJ, Gear, Swash
--   Sylow-7 (F₇): Weiss, Birfield, BendixWeiss, CrossGroove,
--                  Countertrack, SphericalGear
--
-- Per [[168-tower-as-fanout]]: |GL(3, F₂)| = 168 = 2³·3·7 is
-- simple; any generating subset (one Sylow-2 + one Sylow-3 +
-- one Sylow-7 element) generates the full group. Cross-Sylow
-- atlas combinations recover full equivariance even when no
-- single chart does.
--
-- Empirical (II4-II6): cross-Sylow probe pairs exhibit MI
-- supra-additivity. Cardan(S2) ⊗ CrossGroove(S7) gains +1.242
-- bits on substrate_memory; Thompson(S2) ⊗ Tripod(S3) gains
-- +0.440 bits on t1t2. Same-Sylow pairs (Thompson ⊗ Cardan)
-- show ZERO synergy — Sylow-theoretic prediction confirmed.
--
-- Per the user 2026-05-21: 'combinatorial dot product, so we
-- can find which permutations work best with each other'.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Category.AtlasOfProbes where

open import Substrate.Foundation.Nat using (ℕ; zero; suc; _+_; _*_; _≤_; z≤n; s≤s)
open import Data.List using (List; []; _∷_; length)
open import Substrate.Foundation.Product using (_×_; _,_; Σ-syntax)
open import Substrate.Foundation.Eq using (_≡_; refl)

------------------------------------------------------------------------
-- A Sylow class for a probe atlas (2, 3, or 7).

data SylowClass : Set where
  sylow-2 : SylowClass
  sylow-3 : SylowClass
  sylow-7 : SylowClass

------------------------------------------------------------------------
-- A probe is a (chamber-position-offset, V₄-part-extractor) pair.

record Probe : Set₁ where
  field
    offset : ℕ
    -- Stated structurally; the extractor is the V₄-coset position
    -- of the chain symbol at this offset.

open Probe public

------------------------------------------------------------------------
-- A probe atlas is a (Sylow class, ordered list of probes,
-- name) tuple. The list ordering matters for context-value
-- concatenation but the set semantics matters for equivariance
-- — an atlas's structural identity is the SET of offsets
-- (up to a permutation).

record ProbeAtlas : Set₁ where
  field
    name    : List ℕ            -- identifier; concrete instances enumerate
    sylow   : SylowClass
    probes  : List Probe        -- the chart-points

open ProbeAtlas public

------------------------------------------------------------------------
-- The catalog: 16 atlas specifications from the kinematic
-- gauge-sacrifice catalog.
--
-- Each spec has a Sylow-class assignment and a probe-offset
-- pattern. The patterns are parameterised by base primes p, q;
-- the spec records the parametrisation, not the resolved offsets.
--
-- This is stated abstractly; the concrete eliza.probe_atlas
-- runtime resolves specs to numeric offsets.

record AtlasCatalog : Set₂ where
  field
    -- Total number of catalog members.
    catalog-size : ℕ
    -- Per-Sylow-class membership counts.
    n-sylow-2    : ℕ
    n-sylow-3    : ℕ
    n-sylow-7    : ℕ
    -- catalog-size = n-sylow-2 + n-sylow-3 + n-sylow-7
    partition-sums :
      catalog-size ≡ n-sylow-2 + (n-sylow-3 + n-sylow-7)

open AtlasCatalog public

-- Concrete catalog from eliza.probe_atlas (16 = 5 + 5 + 6).

substrate-catalog : AtlasCatalog
substrate-catalog = record
  { catalog-size = 16
  ; n-sylow-2    = 5
  ; n-sylow-3    = 5
  ; n-sylow-7    = 6
  ; partition-sums = refl
  }

------------------------------------------------------------------------
-- Atlas context: the joint product of probe values at a chain
-- position. For an atlas with k probes each contributing a
-- 2-bit V₄-part crumb, the context value is a 2k-bit integer
-- in [0, 4ᵏ).

record AtlasContext (A : ProbeAtlas) : Set₁ where
  field
    Carrier : Set
    -- value-at : chain history index → carrier
    -- Stated abstractly; concrete instances enumerate.

open AtlasContext public

------------------------------------------------------------------------
-- Combinatorial joint context: concatenation of two atlas
-- contexts as a single integer. The "combinatorial dot product"
-- per the user — the Cartesian product of two charts.

record JointContext (A B : ProbeAtlas) : Set₂ where
  field
    ctx-A : AtlasContext A
    ctx-B : AtlasContext B
    -- joint = (ctx-A.value, ctx-B.value) packed bit-wise

open JointContext public

------------------------------------------------------------------------
-- Multi-route equivariance claim.
--
-- Per [[multi-route-equivariance-recovery]]: a joint atlas
-- combining charts from distinct Sylow classes carries
-- predictive information that no single chart does. Empirical
-- (II5):
--   substrate_memory: Cardan (S2) ⊗ CrossGroove (S7) joint MI
--     2.404 bits; max(marginal) = 1.162 bits;
--     synergy = +1.242 bits.
--   t1t2: Thompson (S2) ⊗ Tripod (S3) synergy = +0.440 bits.
--
-- Per Sylow theory: same-Sylow pairs have zero synergy
-- (atlases probe the same Sylow subspace; their joint
-- alphabet doesn't add information). Cross-Sylow pairs probe
-- distinct subspaces and combine multiplicatively.

record SynergyMeasurement (A B : ProbeAtlas) : Set₂ where
  field
    -- MI of A alone, B alone, joint.
    mi-A     : ℕ
    mi-B     : ℕ
    mi-joint : ℕ
    -- Synergy claim: cross-Sylow ⇒ joint > max(marginal)
    -- Stated abstractly; concrete instances enumerate.

open SynergyMeasurement public

------------------------------------------------------------------------
-- The Sylow-collapse observation (II6 empirical).
--
-- Per [[multi-reading-ambient-discipline]] and discrete
-- parameterization: at base primes (p=2, q=3), four atlas
-- specs collapse to identical numeric offset sets:
--   Rzeppa, Gear, BendixWeiss, Countertrack → [2,4,6,8,10,12]
-- This is a parametrization artifact, not a topological
-- equivalence — the kinematic gauge-classes have distinct
-- TOPOLOGICAL structures (Z₃ vs S₃ vs Fano-plane vs antiphase)
-- that linear-period offset patterns don't expose.
--
-- The substrate-honest framing: the linear parametrization
-- here is a starting point; richer probe-geometry (cyclic,
-- projective, sign-alternating) would distinguish the
-- topological classes.

------------------------------------------------------------------------
-- Categorical reading.
--
-- The atlas-of-probes is a FUNCTOR from the category of chain
-- histories to the category of joint context spaces. Each
-- chart (single atlas) is a sub-functor; the full atlas is
-- the colimit of charts.
--
-- Per [[homology-cohomology-recursion]]: chart-level
-- predictions are the homology; the atlas-level joint
-- prediction is the cohomology cycle. Synergy (joint > sum
-- of marginal) IS the cocycle obstruction that the joint
-- atlas resolves.
--
-- Per [[3plus1-parity-universal]]: with three Sylow classes
-- + one chart-orientation chirality, the (S2 ⊕ S3 ⊕ S7) ⊕ F₂
-- = 3+1 structure recurs at the atlas's Sylow-membership level.
--
-- Per [[expose-generator-not-orbit]]: the atlas IS the
-- generator-structure of predictions; reporting any single
-- chart's MI is the orbit-collapse anti-pattern.
------------------------------------------------------------------------
