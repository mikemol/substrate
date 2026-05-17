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

open import Data.Empty using (⊥; ⊥-elim)
open import Data.Nat using (ℕ; zero; suc)
open import Data.Fin using (Fin; zero; suc)
open import Data.Fin.Properties using (_≟_)
open import Data.Product using (_,_)
open import Relation.Binary.PropositionalEquality
  using (_≡_; _≢_; refl; sym; trans; cong)
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
-- transposition-fixes-third: a transposition (i j) fixes any index
-- that's neither i nor j. The 3-cycle pattern relating the three
-- transpositions in S_3 — each fixes its "third" index — IS this
-- helper, instantiated at three (i, j, k) triples whose images
-- under cycle3 form a 3-orbit.
------------------------------------------------------------------------

transposition-fixes-third :
  (i j k : Fin 3) → k ≢ i → k ≢ j →
  SFin.apply (transposition i j) k ≡ k
transposition-fixes-third i j k k≢i k≢j with k ≟ i
... | yes p = ⊥-elim (k≢i p)
... | no _ with k ≟ j
... | yes p = ⊥-elim (k≢j p)
... | no _ = refl

------------------------------------------------------------------------
-- Parametric 3-cycle: a → b → c → a, fix the remaining index.
--
-- Expressed as composition of two transpositions: (a b)(b c). The
-- decomposition (a 1-1 with the second conjugacy class of S_3) is
-- structurally symmetric in (a, b, c) — no chirality choice in the
-- API. When (a, b, c) are not distinct the result is degenerate but
-- still well-typed.
------------------------------------------------------------------------

cycle3 : (a b c : Fin 3) → SFin.Permutation 3
cycle3 a b c = transposition a b SFin.· transposition b c

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

-- 3-cycle (0 1 2): 0↦1, 1↦2, 2↦0.
s3-csw : SFin.Permutation 3
s3-csw = cycle3 zero (suc zero) (suc (suc zero))

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

------------------------------------------------------------------------
-- Inverse direction: SFin.Permutation 3 → OrbitKey.
--
-- Classifies an SFin.Permutation 3 by its action on positions 0 and 1
-- (the third is determined by the permutation's bijectivity). Each of
-- the 6 valid (apply 0, apply 1) pairs maps to a unique OrbitKey; the
-- 3 impossible pairs (apply 0 = apply 1) get an arbitrary default.
------------------------------------------------------------------------

s3-to-orbit-key : SFin.Permutation 3 → OrbitKey
s3-to-orbit-key s with SFin.apply s zero | SFin.apply s (suc zero)
... | zero            | suc zero       = α-pair , even
... | zero            | suc (suc zero) = α-pair , odd
... | suc zero        | suc (suc zero) = β-pair , even
... | suc zero        | zero            = β-pair , odd
... | suc (suc zero)  | zero            = γ-pair , even
... | suc (suc zero)  | suc zero        = γ-pair , odd
... | _               | _               = α-pair , even   -- impossible

------------------------------------------------------------------------
-- Round-trip on the OrbitKey side: s3-to-orbit-key (orbit-key-to-s3 ok) ≡ ok.
-- Each of the 6 cases reduces by computation on the named s3-X elements.
------------------------------------------------------------------------

s3-to-orbit-key-of-orbit-key-to-s3 :
  (ok : OrbitKey) → s3-to-orbit-key (orbit-key-to-s3 ok) ≡ ok
s3-to-orbit-key-of-orbit-key-to-s3 (α-pair , even) = refl
s3-to-orbit-key-of-orbit-key-to-s3 (α-pair , odd)  = refl
s3-to-orbit-key-of-orbit-key-to-s3 (β-pair , even) = refl
s3-to-orbit-key-of-orbit-key-to-s3 (β-pair , odd)  = refl
s3-to-orbit-key-of-orbit-key-to-s3 (γ-pair , even) = refl
s3-to-orbit-key-of-orbit-key-to-s3 (γ-pair , odd)  = refl

-- Helper: SFin.apply is injective (from invₐ + inv-l).
sfin-apply-inj :
  (s : SFin.Permutation 3) {i j : Fin 3} →
  SFin.apply s i ≡ SFin.apply s j → i ≡ j
sfin-apply-inj s {i} {j} eq =
  trans (sym (SFin.inv-l s i)) (trans (cong (SFin.invₐ s) eq) (SFin.inv-l s j))

------------------------------------------------------------------------
-- Pointwise SFin-side round-trip.
--
-- For any s : SFin.Permutation 3, orbit-key-to-s3 (s3-to-orbit-key s)
-- agrees with s on all 3 positions. Proof structure is 3³ = 27 leaves
-- (apply s {0,1,2} each ∈ Fin 3) composed via Fin-3 trichotomy at
-- each level, with 21 leaves killed by bijection-induced injectivity
-- and 6 leaves (one per valid permutation) producing the equality
-- by refl / sym pᵢ.
--
-- The composition shape: outer trichotomy on apply s 0 (3 ways),
-- middle trichotomy on apply s 1 (3 ways, 1-impossible-per-outer
-- via injectivity), inner trichotomy on apply s 2 (3 ways, 2-
-- impossible-per-(outer,middle) via injectivity, 1 producing the
-- result). The 27 leaves are NOT written out individually here;
-- they emerge from the trichotomy composition + Fin-equality
-- patterns.
------------------------------------------------------------------------

-- Witnesses of Fin 3 inequality used to discharge impossible cases.
-- Fully-typed via `_≢_ {A = Fin 3}` to prevent index-ambiguity when
-- used inside sfin-apply-inj.
private
  0≢1 : _≢_ {A = Fin 3} zero (suc zero)
  0≢1 ()
  2≢0 : _≢_ {A = Fin 3} (suc (suc zero)) zero
  2≢0 ()
  2≢1 : _≢_ {A = Fin 3} (suc (suc zero)) (suc zero)
  2≢1 ()

orbit-key-to-s3-of-s3-to-orbit-key :
  (s : SFin.Permutation 3) (i : Fin 3) →
  SFin.apply (orbit-key-to-s3 (s3-to-orbit-key s)) i ≡ SFin.apply s i
orbit-key-to-s3-of-s3-to-orbit-key s i
  with SFin.apply s zero in p0 | SFin.apply s (suc zero) in p1
-- The 3 (apply 0 = apply 1) cases die immediately by injectivity.
... | zero | zero =
  ⊥-elim (0≢1 (sfin-apply-inj s (trans p0 (sym p1))))
... | suc zero | suc zero =
  ⊥-elim (0≢1 (sfin-apply-inj s (trans p0 (sym p1))))
... | suc (suc zero) | suc (suc zero) =
  ⊥-elim (0≢1 (sfin-apply-inj s (trans p0 (sym p1))))
-- The 6 valid cases. Each branch reduces orbit-key-to-s3 (s3-to-orbit-
-- key s) to a specific named s3-X, whose apply behaviour at positions
-- 0 and 1 matches s by construction (refl after rewriting); position 2
-- is determined by trichotomy on apply s 2 with 2 impossible sub-cases.
... | zero | suc zero       = α-even-case i
  where
    α-even-case : (i : Fin 3) → SFin.apply (orbit-key-to-s3 (α-pair , even)) i ≡ SFin.apply s i
    α-even-case zero            = sym p0
    α-even-case (suc zero)      = sym p1
    α-even-case (suc (suc zero)) with SFin.apply s (suc (suc zero)) in p2
    ... | zero            = ⊥-elim (2≢0 (sfin-apply-inj s (trans p2 (sym p0))))
    ... | suc zero        = ⊥-elim (2≢1 (sfin-apply-inj s (trans p2 (sym p1))))
    ... | suc (suc zero)  = refl
... | zero | suc (suc zero) = α-odd-case i
  where
    α-odd-case : (i : Fin 3) → SFin.apply (orbit-key-to-s3 (α-pair , odd)) i ≡ SFin.apply s i
    α-odd-case zero            = sym p0
    α-odd-case (suc zero)      = sym p1
    α-odd-case (suc (suc zero)) with SFin.apply s (suc (suc zero)) in p2
    ... | zero            = ⊥-elim (2≢0 (sfin-apply-inj s (trans p2 (sym p0))))
    ... | suc zero        = refl
    ... | suc (suc zero)  = ⊥-elim (2≢1 (sfin-apply-inj s (trans p2 (sym p1))))
... | suc zero | zero       = β-odd-case i
  where
    β-odd-case : (i : Fin 3) → SFin.apply (orbit-key-to-s3 (β-pair , odd)) i ≡ SFin.apply s i
    β-odd-case zero            = sym p0
    β-odd-case (suc zero)      = sym p1
    β-odd-case (suc (suc zero)) with SFin.apply s (suc (suc zero)) in p2
    ... | zero            = ⊥-elim (2≢1 (sfin-apply-inj s (trans p2 (sym p1))))
    ... | suc zero        = ⊥-elim (2≢0 (sfin-apply-inj s (trans p2 (sym p0))))
    ... | suc (suc zero)  = refl
... | suc zero | suc (suc zero) = β-even-case i
  where
    β-even-case : (i : Fin 3) → SFin.apply (orbit-key-to-s3 (β-pair , even)) i ≡ SFin.apply s i
    β-even-case zero            = sym p0
    β-even-case (suc zero)      = sym p1
    β-even-case (suc (suc zero)) with SFin.apply s (suc (suc zero)) in p2
    ... | zero            = refl
    ... | suc zero        = ⊥-elim (2≢0 (sfin-apply-inj s (trans p2 (sym p0))))
    ... | suc (suc zero)  = ⊥-elim (2≢1 (sfin-apply-inj s (trans p2 (sym p1))))
... | suc (suc zero) | zero = γ-even-case i
  where
    γ-even-case : (i : Fin 3) → SFin.apply (orbit-key-to-s3 (γ-pair , even)) i ≡ SFin.apply s i
    γ-even-case zero            = sym p0
    γ-even-case (suc zero)      = sym p1
    γ-even-case (suc (suc zero)) with SFin.apply s (suc (suc zero)) in p2
    ... | zero            = ⊥-elim (2≢1 (sfin-apply-inj s (trans p2 (sym p1))))
    ... | suc zero        = refl
    ... | suc (suc zero)  = ⊥-elim (2≢0 (sfin-apply-inj s (trans p2 (sym p0))))
... | suc (suc zero) | suc zero = γ-odd-case i
  where
    γ-odd-case : (i : Fin 3) → SFin.apply (orbit-key-to-s3 (γ-pair , odd)) i ≡ SFin.apply s i
    γ-odd-case zero            = sym p0
    γ-odd-case (suc zero)      = sym p1
    γ-odd-case (suc (suc zero)) with SFin.apply s (suc (suc zero)) in p2
    ... | zero            = refl
    ... | suc zero        = ⊥-elim (2≢1 (sfin-apply-inj s (trans p2 (sym p1))))
    ... | suc (suc zero)  = ⊥-elim (2≢0 (sfin-apply-inj s (trans p2 (sym p0))))
