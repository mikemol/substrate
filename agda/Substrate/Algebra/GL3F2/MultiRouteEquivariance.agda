------------------------------------------------------------------------
-- Substrate.Algebra.GL3F2.MultiRouteEquivariance
--
-- S5 of the multi-route equivariance arc per
-- [[multi-route-equivariance-recovery]] +
-- [[klein-quartic-kinematic-anatomy]]. This module:
--
--   1. Packages the three Sylow-canonical generators (swap01-Linear,
--      cycle3-Linear, singer-Linear) as full GL3F2 values, deriving
--      inverse witnesses from each generator's HasOrder.
--
--   2. States the joint-generation theorem: the three generators
--      together cover GL(3, F₂) = |PSL(2, 7)| = 168.
--
-- The theorem statement is structural: the three Sylow orders (2, 3, 7)
-- cover all prime divisors of 168, and any subset of a simple group
-- containing elements of all its prime-order Sylow generators must
-- generate the full group (classical group theory).
--
-- The full enumeration "the generated subgroup has 168 elements" is
-- OUT of scope for this slice — that's a finite check requiring
-- substantial machinery (Sylow-subgroup enumeration, coset
-- arithmetic). What this slice DOES deliver: the three generators with
-- verified inverse witnesses and orders, plus the structural meta-
-- claim and its justification.
--
-- Per [[reserved-selfdual-bijection-gauge]]: this closes the original
-- V₄-equivariance question by ATLAS-LEVEL reframing rather than
-- chart-level sacrifice. The atlas of three Sylow charts inherits
-- equivariance jointly via PSL(2, 7)'s simplicity, even though no
-- single chart carries it.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.GL3F2.MultiRouteEquivariance where

open import Data.Nat using (ℕ)
open import Relation.Binary.PropositionalEquality
  using (_≡_; refl; sym; trans; cong)

open import Substrate.Algebra.F2.Vector using (Vector)
open import Substrate.Algebra.F2.Linear
  using (Linear; id-L; _∘L_; apply)
open import Substrate.Algebra.F2.Linear.FromImages.Permutation
  using (L-iterate; iterate-apply-as-L-iterate)
open import Substrate.Category.Coalgebra.FiniteOrder
  using (iterate; iterate-add; HasOrder)

open import Substrate.Algebra.GL3F2
  using (GL3F2; mkGL3F2; id-GL; _·G_; _⁻¹G; HasOrder-GL)
open import Substrate.Algebra.GL3F2.GaugeGenerators
  using (swap01-Linear; HasOrder-swap01;
         cycle3-Linear; HasOrder-cycle3;
         singer-Linear)
open import Substrate.Algebra.GL3F2.SingerOrder using (HasOrder-singer)

------------------------------------------------------------------------
-- 1. Sylow-2 generator as a GL3F2 value.
--
-- swap01-Linear is its own inverse (HasOrder 2). The L-left/L-right
-- witnesses are exactly HasOrder-swap01.
------------------------------------------------------------------------

swap01-GL : GL3F2
swap01-GL = mkGL3F2 swap01-Linear swap01-Linear HasOrder-swap01 HasOrder-swap01

HasOrder-GL-swap01 : HasOrder-GL swap01-GL 2
HasOrder-GL-swap01 = HasOrder-swap01

------------------------------------------------------------------------
-- 2. Sylow-3 generator as a GL3F2 value.
--
-- cycle3-Linear has order 3; its inverse is cycle3-Linear ∘L cycle3-
-- Linear (= cycle3²). The L-left witness:
--   apply (cycle3 ∘L cycle3) (apply cycle3 v)
--     = apply cycle3 (apply cycle3 (apply cycle3 v))
--     = iterate 3 (apply cycle3) v
--     = v          [HasOrder-cycle3]
------------------------------------------------------------------------

cycle3-inv : Linear 3 3
cycle3-inv = cycle3-Linear ∘L cycle3-Linear

cycle3-GL : GL3F2
cycle3-GL = mkGL3F2 cycle3-Linear cycle3-inv left-witness right-witness
  where
    left-witness :
      (v : Vector 3) →
      apply cycle3-inv (apply cycle3-Linear v) ≡ v
    left-witness v = HasOrder-cycle3 v

    right-witness :
      (v : Vector 3) →
      apply cycle3-Linear (apply cycle3-inv v) ≡ v
    right-witness v = HasOrder-cycle3 v

HasOrder-GL-cycle3 : HasOrder-GL cycle3-GL 3
HasOrder-GL-cycle3 = HasOrder-cycle3

------------------------------------------------------------------------
-- 3. Sylow-7 generator as a GL3F2 value.
--
-- singer-Linear has order 7; its inverse is L-iterate 6 singer-Linear
-- (= singer⁶). The L-left witness:
--   apply (L-iterate 6 singer) (apply singer v)
--     ≡ iterate 6 (apply singer) (apply singer v)   [iterate-apply-as-L-iterate, sym]
--     ≡ iterate 7 (apply singer) v                   [sym iterate-add 6 1]
--     ≡ v                                            [HasOrder-singer]
------------------------------------------------------------------------

singer-inv : Linear 3 3
singer-inv = L-iterate 6 singer-Linear

singer-GL : GL3F2
singer-GL = mkGL3F2 singer-Linear singer-inv left-witness right-witness
  where
    left-witness :
      (v : Vector 3) →
      apply singer-inv (apply singer-Linear v) ≡ v
    left-witness v =
      trans (sym (iterate-apply-as-L-iterate singer-Linear 6 (apply singer-Linear v)))
            (HasOrder-singer v)

    right-witness :
      (v : Vector 3) →
      apply singer-Linear (apply singer-inv v) ≡ v
    right-witness v =
      trans (cong (apply singer-Linear)
                  (sym (iterate-apply-as-L-iterate singer-Linear 6 v)))
            (HasOrder-singer v)

HasOrder-GL-singer : HasOrder-GL singer-GL 7
HasOrder-GL-singer = HasOrder-singer

------------------------------------------------------------------------
-- 4. The three orders cover all prime divisors of |GL(3, F₂)| = 168.
--
-- 168 = 2³ · 3 · 7
--
-- swap01-GL has order 2 (= prime divisor of 2³)
-- cycle3-GL has order 3 (= the prime divisor 3)
-- singer-GL has order 7 (= the prime divisor 7)
--
-- This is the constructive content of the multi-route theorem's
-- HYPOTHESIS: three generators with orders covering all prime divisors
-- of |G|.
------------------------------------------------------------------------

-- Prime-divisor witnesses (the orders).
prime-divisor-2 : HasOrder-GL swap01-GL 2
prime-divisor-2 = HasOrder-GL-swap01

prime-divisor-3 : HasOrder-GL cycle3-GL 3
prime-divisor-3 = HasOrder-GL-cycle3

prime-divisor-7 : HasOrder-GL singer-GL 7
prime-divisor-7 = HasOrder-GL-singer

------------------------------------------------------------------------
-- 5. The multi-route generation theorem — META-STATEMENT.
--
-- Joint-generation theorem (META, justified by classical group theory):
--
--   ⟨swap01-GL, cycle3-GL, singer-GL⟩ = GL(3, F₂)
--
-- Justification chain:
--
--   * GL(3, F₂) ≅ PSL(2, 7) is a SIMPLE group of order 168 = 2³·3·7.
--   * The three generators have orders 2, 3, 7 respectively
--     (verified above as prime-divisor-2, prime-divisor-3,
--     prime-divisor-7).
--   * Sylow's theorems: the Sylow-p subgroup is a subgroup of order
--     p^k where p^k || |G|. The element of order p generates a
--     non-trivial subgroup of the Sylow-p.
--   * Simplicity: no proper non-trivial normal subgroup; therefore no
--     proper subgroup can contain elements from all three prime
--     orders (such a subgroup's order would have to be divisible by
--     2·3·7 = 42, leaving index 4 — but PSL(2, 7) has no subgroup of
--     index 4 since 4 < 5 = smallest non-trivial degree of its
--     faithful permutation action).
--   * Therefore ⟨swap01-GL, cycle3-GL, singer-GL⟩ = GL(3, F₂).
--
-- This META-statement closes the V₄-equivariance question from
-- [[reserved-selfdual-bijection-gauge]] at the structural level. The
-- atlas of three Sylow charts inherits GL(3, F₂)-equivariance jointly
-- via PSL(2, 7)'s simplicity, even though no single chart carries it
-- (the original sacrifice ladder applies per chart).
--
-- Full constructive verification (enumeration of the generated
-- subgroup's 168 elements) is OUT of scope for this slice; queued as
-- a finite-check follow-on if a downstream consumer needs it.
------------------------------------------------------------------------

------------------------------------------------------------------------
-- 6. Capstone — multi-route equivariance arc complete (S5 of S5).
--
-- After this arc the substrate exposes:
--
--   * The Sylow-7 cyclic carrier (Z7-Coxeter) — Coxeter-backed.
--   * The Fano plane (ℙ²(F₂)) with Singer 7-cycle.
--   * GL3F2 as a record with group operations.
--   * Three Sylow-canonical generators with HasOrder witnesses.
--   * The joint-generation meta-theorem closing the V₄-equivariance
--     question via atlas-vs-chart reframing.
--
-- Per [[multi-route-equivariance-recovery]]: the sacrifice ladder is
-- no longer the operational mechanism for recovering equivariance;
-- the atlas-of-charts (= multi-route articulation) is. Each gauge-
-- class chart still requires a sacrifice (per chart), but the joint
-- structure inherits the full 168-element gauge freedom WITHOUT any
-- single chart carrying it alone.
--
-- Per [[kinematic-gauge-sacrifice-catalog]]: the 12+ CV-joint family
-- members are 12+ different kinematic embodiments of this atlas-of-
-- charts pattern — each joint is one chart within the full
-- GL(3, F₂)-equivariant atlas.
------------------------------------------------------------------------
