------------------------------------------------------------------------
-- Substrate.Algebra.GL3F2.GaugeGenerators
--
-- The three Sylow-canonical generators of GL(3, F₂), per
-- [[klein-quartic-kinematic-anatomy]] + [[multi-route-equivariance-
-- recovery]]:
--
--   * Sylow-2 (order 2): swap01-Linear — a basis transposition,
--     anchoring the flag-stabilizer family of Sylow-2 elements
--     (Thompson, Double Cardan, Cornay, Rag joint kinematic class).
--
--   * Sylow-3 (order 3): cycle3-Linear — the 3-cycle on basis
--     vectors, anchoring the cyclic-coordinate-permutation family
--     (Rzeppa, Tripod, Double Offset, Gear coupling class).
--
--   * Sylow-7 (order 7): singer-Linear — multiplication by x in
--     F₂[x]/(x³+x+1), anchoring the Singer-cyclic-tricycle family
--     (Weiss, Birfield, Bendix-Weiss, Cross-Groove, Countertrack
--     class).
--
-- This file delivers the three Linear values plus HasOrder witnesses
-- for Sylow-2 and Sylow-3 (mechanical via existing HasOrder-from-perm
-- combinator). HasOrder-singer (the order-7 proof for the Sylow-7
-- generator) is its own follow-on slice
-- (Substrate.Algebra.GL3F2.SingerOrder) because the proof is non-
-- mechanical (singer is not a basis permutation, so HasOrder-from-perm
-- doesn't apply; basis-level computation via linear-extensionality is
-- needed).
--
-- After both slices (Generators + SingerOrder), the three generators
-- can be packaged as GL3F2 values with full inverse witnesses for the
-- multi-route generation theorem in S5.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.GL3F2.GaugeGenerators where

open import Substrate.Foundation.Fin.Fin
open import Substrate.Foundation.Fin.Literals using (₁; ₂; ₃; ₈; ₁₂)
open import Substrate.Foundation.Eq using (_≡_; refl)

open import Substrate.Algebra.F2.Linear using (Linear; apply)
open import Substrate.Algebra.F2.Linear.FromImages.Permutation.Linear using (basis-permutation-Linear)
open import Substrate.Algebra.F2.Linear.FromImages.Permutation.Order using (HasOrder-from-perm)
open import Substrate.Foundation.Fin.Iterate using (HasOrderPerm)
open import Substrate.Algebra.F2.Linear.FromImages.Permutation.Cyclic using (cyclic-Linear; cyclic-HasOrder)
open import Substrate.Algebra.Nat.CyclicSuc using (cyclic-suc)
open import Substrate.Algebra.F2.FanoPlane
  using (singer-Linear) public
open import Substrate.Category.Coalgebra.FiniteOrder using (HasOrder)

------------------------------------------------------------------------
-- 1. Sylow-2 generator: swap01-Linear.
--
-- The basis transposition σ₂ : Fin 3 → Fin 3 swaps 0 ↔ 1 and fixes 2.
-- Its lift via basis-permutation-Linear is a self-inverse linear map
-- on Vector 3 (= an involution). One concrete element of the Sylow-2
-- subgroup of GL(3, F₂); the flag stabilizer of basis 2.
------------------------------------------------------------------------

σ₂ : Fin 3 → Fin 3
σ₂ zero             = suc zero
σ₂ ₁       = zero
σ₂ ₂ = suc ₁

σ₂-HasOrderPerm : HasOrderPerm σ₂ 2
σ₂-HasOrderPerm zero             = refl
σ₂-HasOrderPerm ₁       = refl
σ₂-HasOrderPerm ₂ = refl

swap01-Linear : Linear 3 3
swap01-Linear = basis-permutation-Linear σ₂

HasOrder-swap01 : HasOrder (apply swap01-Linear) 2
HasOrder-swap01 = HasOrder-from-perm σ₂ 2 σ₂-HasOrderPerm

------------------------------------------------------------------------
-- 2. Sylow-3 generator: cycle3-Linear.
--
-- σ₃ : Fin 3 → Fin 3 cycles basis vectors as 0 → 1 → 2 → 0.
-- cycle3-Linear = the basis-permutation Linear of σ₃, order 3 — a known
-- element of the Sylow-3 subgroup of GL(3, F₂).
--
-- Ⓖ.cyclen-collapse-registry (2026-07-05): these WERE re-exported from the
-- standalone per-n module ...Permutation.Cycle3 (a thin σ₃ = cyclic-suc {2}
-- renaming). That obsolete orbit-module is now dissolved; the Sylow-3
-- generator lives HERE, in its canonical registry home alongside the Sylow-2
-- (σ₂/swap01-Linear) and Sylow-7 (singer-Linear) generators, each derived
-- directly from the parametric Cyclic.{cyclic-suc, cyclic-Linear,
-- cyclic-HasOrder} at n = 2 (the [[expose-generator-not-orbit]] collapse).
------------------------------------------------------------------------

σ₃ : Fin 3 → Fin 3
σ₃ = cyclic-suc {2}

cycle3-Linear : Linear 3 3
cycle3-Linear = cyclic-Linear {2}

HasOrder-cycle3 : HasOrder (apply cycle3-Linear) 3
HasOrder-cycle3 = cyclic-HasOrder {2}

------------------------------------------------------------------------
-- 3. Sylow-7 generator: singer-Linear (re-exported from FanoPlane).
--
-- singer-Linear : Linear 3 3 is the linear extension of the basis
-- images
--   basis 0 ↦ basis 1   (= e₂)
--   basis 1 ↦ basis 2   (= e₃)
--   basis 2 ↦ basis 0 +ⱽ basis 1   (= e₁₂)
-- — multiplication by x in F₈ = F₂[x]/(x³+x+1). It permutes the 7
-- nonzero vectors of F₂³ (= Fano-plane points) in a single 7-cycle.
--
-- HasOrder-singer (the order-7 witness) is the deliverable of
-- Substrate.Algebra.GL3F2.SingerOrder (queued follow-on). Once landed,
-- the three generators are packaged as GL3F2 values for S5.
------------------------------------------------------------------------

-- (no new declarations — see imports for singer-Linear; HasOrder-singer
-- arrives via SingerOrder)
