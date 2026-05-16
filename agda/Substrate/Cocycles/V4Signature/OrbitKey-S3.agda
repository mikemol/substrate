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

open import Data.Empty using (⊥-elim)
open import Data.Nat using (ℕ; zero; suc)
open import Data.Fin using (Fin; zero; suc)
open import Data.Fin.Properties using (_≟_)
open import Data.Product using (_,_)
open import Relation.Binary.PropositionalEquality
  using (_≡_; refl)
open import Relation.Nullary using (yes; no)

import Substrate.Groups.SFin as SFin
open import Substrate.Cocycles.V4Signature
  using (Pairing; α-pair; β-pair; γ-pair;
         Chirality; even; odd;
         OrbitKey)

------------------------------------------------------------------------
-- Parametric transposition: given i, j : Fin 3, swap them (fix the
-- third index).
--
-- Symmetric in (i, j) — no chirality-choice generators. Each of the
-- 3 transpositions in S_3 is an instance with specific indices.
-- Per [[feedback-choice-rigidification-in-substrate]]: avoid picking
-- canonical generators; expand the cohomological structure (S_3's
-- transposition conjugacy class is a 3-element orbit under S_3
-- conjugation) and genericize over the class.
--
-- When i ≡ j the result is the identity (no swap to perform).
------------------------------------------------------------------------

transposition : (i j : Fin 3) → SFin.Permutation 3
transposition i j = record
  { apply  = swap-fn
  ; invₐ   = swap-fn
  ; inv-l  = swap-invo
  ; inv-r  = swap-invo
  }
  where
    swap-fn : Fin 3 → Fin 3
    swap-fn k with k ≟ i
    ... | yes _ = j
    ... | no _ with k ≟ j
    ...           | yes _ = i
    ...           | no _  = k

    -- swap-fn is self-inverse: swapping twice recovers the original.
    -- Case analysis on (k ≟ i, k ≟ j); the dispatch in swap-fn drives
    -- the case-tree.
    swap-invo : (k : Fin 3) → swap-fn (swap-fn k) ≡ k
    swap-invo k with k ≟ i
    ... | yes refl with j ≟ i
    ...               | yes refl = refl
    ...               | no _ with j ≟ j
    ...                          | yes _ = refl
    ...                          | no q = ⊥-elim (q refl)
    swap-invo k | no q1 with k ≟ j
    ... | yes refl with i ≟ i
    ...               | yes _ = refl
    ...               | no q = ⊥-elim (q refl)
    swap-invo k | no q1 | no q2 with k ≟ i
    ... | yes a = ⊥-elim (q1 a)
    ... | no _ with k ≟ j
    ...           | yes b = ⊥-elim (q2 b)
    ...           | no _ = refl

------------------------------------------------------------------------
-- The 6 elements of SFin.Permutation 3.
------------------------------------------------------------------------

-- Identity: just SFin.ε.
s3-id : SFin.Permutation 3
s3-id = SFin.ε

-- swap (1 2): 0↦0, 1↦2, 2↦1. Now an instance of `transposition`.
s3-sw : SFin.Permutation 3
s3-sw = transposition (suc zero) (suc (suc zero))

-- swap (0 1): 0↦1, 1↦0, 2↦2.
s3-cs : SFin.Permutation 3
s3-cs = transposition zero (suc zero)

-- swap (0 2): 0↦2, 1↦1, 2↦0.
s3-cw : SFin.Permutation 3
s3-cw = transposition zero (suc (suc zero))

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

-- 3-cycle (0 2 1): 0↦2, 1↦0, 2↦1. Inverse: (0 1 2) = s3-csw.
-- Defined via SFin._⁻¹ to collapse the {s3-csw, s3-cws} 2-orbit
-- surfaced by `scratch/findings.py` — the orbit detector identified
-- that s3-cws is structurally the inverse of s3-csw modulo a single
-- substitution, and the swap of (apply, invₐ) is exactly what
-- SFin._⁻¹ provides.
s3-cws : SFin.Permutation 3
s3-cws = s3-csw SFin.⁻¹

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
