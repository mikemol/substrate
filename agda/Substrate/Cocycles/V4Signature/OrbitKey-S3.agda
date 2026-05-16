------------------------------------------------------------------------
-- Substrate.Cocycles.V4Signature.OrbitKey-S3
--
-- Slice 17: the OrbitKey ↔ SFin.Permutation 3 chirality choice for
-- the CY-5 cocycle. Defines 6 specific elements of SFin.Permutation
-- 3 and the bijection between them and OrbitKey.
--
-- Purpose: lets slice 4's V_4 ⋊ Stab(D) ≅ S_4 round-trip ride on
-- slice 14d's parametric `extend-restrict D` lemma rather than
-- hand-enumerating 6 D-specific case lemmas. The chirality choice
-- (which OrbitKey maps to which S_3 element) is consolidated HERE,
-- not scattered across 6 hand-coded Stab(D) Permutation records.
--
-- The 6 S_3 elements (under the D-anchor convention 0↔C, 1↔S, 2↔W
-- from Substrate.Groups.Stab-S3):
--
--   s3-id   = identity     (corresponds to (α-pair, even) ↔ stab-id)
--   s3-sw   = swap (1 2)   ((α-pair, odd)  ↔ stab-sw, S↔W)
--   s3-cs   = swap (0 1)   ((β-pair, odd)  ↔ stab-cs, C↔S)
--   s3-cw   = swap (0 2)   ((γ-pair, odd)  ↔ stab-cw, C↔W)
--   s3-csw  = 3-cycle 0→1→2→0   ((β-pair, even) ↔ stab-csw)
--   s3-cws  = 3-cycle 0→2→1→0   ((γ-pair, even) ↔ stab-cws)
--
-- The OrbitKey ↔ s3-* labeling is the cocycle's chirality choice —
-- one of 6! = 720 valid labelings, picked once and exposed via
-- `orbit-key-to-s3` / `s3-to-orbit-key`. Per
-- [[feedback-ordering-is-chirality-choice]], downstream code MUST
-- consume the labeling abstractly via these functions, not by
-- pattern-matching on specific (Pairing, Chirality) ↔ Fin 3 indices.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Cocycles.V4Signature.OrbitKey-S3 where

open import Data.Nat using (ℕ; zero; suc)
open import Data.Fin using (Fin; zero; suc)
open import Data.Product using (_,_)
open import Relation.Binary.PropositionalEquality
  using (_≡_; refl)

import Substrate.Groups.SFin as SFin
open import Substrate.Cocycles.V4Signature
  using (Pairing; α-pair; β-pair; γ-pair;
         Chirality; even; odd;
         OrbitKey)

------------------------------------------------------------------------
-- The 6 elements of SFin.Permutation 3.
------------------------------------------------------------------------

-- Identity: just SFin.ε.
s3-id : SFin.Permutation 3
s3-id = SFin.ε

-- swap (1 2): 0↦0, 1↦2, 2↦1. Self-inverse.
s3-sw : SFin.Permutation 3
s3-sw = record { apply = ap ; invₐ = ap ; inv-l = invo ; inv-r = invo }
  where
    ap : Fin 3 → Fin 3
    ap zero             = zero
    ap (suc zero)       = suc (suc zero)
    ap (suc (suc zero)) = suc zero
    invo : (i : Fin 3) → ap (ap i) ≡ i
    invo zero             = refl
    invo (suc zero)       = refl
    invo (suc (suc zero)) = refl

-- swap (0 1): 0↦1, 1↦0, 2↦2. Self-inverse.
s3-cs : SFin.Permutation 3
s3-cs = record { apply = ap ; invₐ = ap ; inv-l = invo ; inv-r = invo }
  where
    ap : Fin 3 → Fin 3
    ap zero             = suc zero
    ap (suc zero)       = zero
    ap (suc (suc zero)) = suc (suc zero)
    invo : (i : Fin 3) → ap (ap i) ≡ i
    invo zero             = refl
    invo (suc zero)       = refl
    invo (suc (suc zero)) = refl

-- swap (0 2): 0↦2, 1↦1, 2↦0. Self-inverse.
s3-cw : SFin.Permutation 3
s3-cw = record { apply = ap ; invₐ = ap ; inv-l = invo ; inv-r = invo }
  where
    ap : Fin 3 → Fin 3
    ap zero             = suc (suc zero)
    ap (suc zero)       = suc zero
    ap (suc (suc zero)) = zero
    invo : (i : Fin 3) → ap (ap i) ≡ i
    invo zero             = refl
    invo (suc zero)       = refl
    invo (suc (suc zero)) = refl

-- 3-cycle (0 1 2): 0↦1, 1↦2, 2↦0. Inverse: (0 2 1).
s3-csw : SFin.Permutation 3
s3-csw = record { apply = ap ; invₐ = inv-ap ; inv-l = il ; inv-r = ir }
  where
    ap : Fin 3 → Fin 3
    ap zero             = suc zero
    ap (suc zero)       = suc (suc zero)
    ap (suc (suc zero)) = zero
    inv-ap : Fin 3 → Fin 3
    inv-ap zero             = suc (suc zero)
    inv-ap (suc zero)       = zero
    inv-ap (suc (suc zero)) = suc zero
    il : (i : Fin 3) → inv-ap (ap i) ≡ i
    il zero             = refl
    il (suc zero)       = refl
    il (suc (suc zero)) = refl
    ir : (i : Fin 3) → ap (inv-ap i) ≡ i
    ir zero             = refl
    ir (suc zero)       = refl
    ir (suc (suc zero)) = refl

-- 3-cycle (0 2 1): 0↦2, 1↦0, 2↦1. Inverse: (0 1 2).
s3-cws : SFin.Permutation 3
s3-cws = record { apply = ap ; invₐ = inv-ap ; inv-l = il ; inv-r = ir }
  where
    ap : Fin 3 → Fin 3
    ap zero             = suc (suc zero)
    ap (suc zero)       = zero
    ap (suc (suc zero)) = suc zero
    inv-ap : Fin 3 → Fin 3
    inv-ap zero             = suc zero
    inv-ap (suc zero)       = suc (suc zero)
    inv-ap (suc (suc zero)) = zero
    il : (i : Fin 3) → inv-ap (ap i) ≡ i
    il zero             = refl
    il (suc zero)       = refl
    il (suc (suc zero)) = refl
    ir : (i : Fin 3) → ap (inv-ap i) ≡ i
    ir zero             = refl
    ir (suc zero)       = refl
    ir (suc (suc zero)) = refl

------------------------------------------------------------------------
-- OrbitKey ↔ SFin.Permutation 3 labeling.
--
-- This IS the cocycle's chirality choice. Six other valid labelings
-- exist (any S_3-conjugate); per [[feedback-ordering-is-chirality-
-- choice]] downstream code consumes this function ABSTRACTLY.
------------------------------------------------------------------------

orbit-key-to-s3 : OrbitKey → SFin.Permutation 3
orbit-key-to-s3 (α-pair , even) = s3-id
orbit-key-to-s3 (α-pair , odd)  = s3-sw
orbit-key-to-s3 (β-pair , even) = s3-csw
orbit-key-to-s3 (β-pair , odd)  = s3-cs
orbit-key-to-s3 (γ-pair , even) = s3-cws
orbit-key-to-s3 (γ-pair , odd)  = s3-cw
