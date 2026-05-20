------------------------------------------------------------------------
-- Eliza.Alphabets
--
-- The four alphabets the pipeline transduces between.
--
--   * Char    — raw input. Postulated (the full Unicode range is out
--               of scope for the skeleton; only the per-symbol routing
--               behaviour matters).
--
--   * Gen     — Coxeter generators of S₄ as a Coxeter system A₃:
--               s₁, s₂, s₃, the simple reflections.
--
--   * Chamber — elements of S₄. The 24 chambers of the A₃ Coxeter
--               complex. Postulated as a concrete finite set of 24
--               with named extremes (origin e, antipode w₀).
--
--   * Orbit   — V₄-cosets in S₄. The Cocycle invariant per
--               Substrate.Cocycles.V4Signature. Six in total, split
--               by Pairing × Chirality.
--
-- The Pairing × Chirality split is fundamental: it is the substrate's
-- 3+1 parity universal applied at this level (3 Pairings — the V₄-axis
-- partitions of {1,2,3,4} — times 2 Chiralities — A₄ coset / non-coset).
------------------------------------------------------------------------

{-# OPTIONS --without-K #-}

module Eliza.Alphabets where

open import Eliza.Prelude using (_×_)

------------------------------------------------------------------------
-- 1. Char — postulated.
------------------------------------------------------------------------

postulate
  Char : Set

------------------------------------------------------------------------
-- 2. Gen — the three simple reflections.
------------------------------------------------------------------------

data Gen : Set where
  s₁ s₂ s₃ : Gen

------------------------------------------------------------------------
-- 3. Chamber — postulated as an abstract type with named extremes and
-- a decidable-equality witness (postulated). The concrete bijection
-- to 4-tuples lives in the Python; the Agda skeleton only commits to
-- "there is such a finite set with these named points."
------------------------------------------------------------------------

postulate
  Chamber : Set
  e       : Chamber   -- the origin / identity
  w₀      : Chamber   -- the longest word / antipode
  _≟C_    : Chamber → Chamber → Set  -- decidable equality; sketch only

------------------------------------------------------------------------
-- 4. Pairing × Chirality. The two factors of the Orbit invariant.
------------------------------------------------------------------------

data Pairing : Set where
  α-pair β-pair γ-pair : Pairing

data Chirality : Set where
  even odd : Chirality

------------------------------------------------------------------------
-- 5. Orbit — the V₄-coset, named exactly per Cocycles.V4Signature.
------------------------------------------------------------------------

Orbit : Set
Orbit = Pairing × Chirality

------------------------------------------------------------------------
-- 6. The four V₄ elements as a separate atomic type. The "fiber" of
-- the cocycle: which position within the orbit the chamber sits at.
--
-- e₄ = identity, α/β/γ = the three (involutive) products-of-disjoint-
-- transpositions.
------------------------------------------------------------------------

data V₄ : Set where
  e₄ α β γ : V₄
