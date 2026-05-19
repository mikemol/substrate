------------------------------------------------------------------------
-- Substrate.Groups.Z3-x-FreeCyclic
--
-- The 2-D word algebra Z₃ × ℕ via DirectProduct of Z₃-Coxeter and
-- FreeCyclic-Coxeter.
--
-- This is the substrate-native universal-cover-style construction for
-- Z/3: the phase axis (Z₃-Coxeter, cyclic of order 3) paired with a
-- cycle counter axis (FreeCyclic-Coxeter, infinite-order ℕ-like).
--
-- Words are pairs (phase-word, cycle-word). All operations
-- componentwise via the Coxeter framework's DirectProduct combinator:
-- _·_ pairs the products, normalize pairs the normalizations, etc.
--
-- The phase-projection (slice 4) "forgets" the cycle counter,
-- recovering the original Z₃. The cycle-projection extracts how many
-- full cycles deep — exactly the "cover map's ℕ component."
--
-- Per [[feedback-roll-our-own-via-word-algebra]]: substrate-native
-- 2-D word algebra. The orthogonal dimension (cycle count) is
-- explicit; the modular reading (phase) is the quotient. Together
-- they form the universal cover ℤ → Z/3 (or in the monoid case,
-- ℕ → Z/3).
--
-- Per the 2-D word algebra arc: instance #1 (n=3).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Groups.Z3-x-FreeCyclic where

import Substrate.Groups.Z3-Coxeter as Z₃
import Substrate.Groups.FreeCyclic-Coxeter as F

------------------------------------------------------------------------
-- Instantiate DirectProduct: phase = Z₃, cycle = FreeCyclic.
--
-- Mirror of V4-as-Z2xZ2's instantiation. The DirectProduct combinator
-- takes both components' Core inputs and produces the combined
-- Coxeter Core for the 2-D algebra.
------------------------------------------------------------------------

open import Substrate.Groups.Coxeter.DirectProduct
  -- Phase component: Z₃-Coxeter.
  (Z₃.Word Z₃.Gen) (Z₃._++_) Z₃.ε Z₃.++-assoc
    Z₃.Canonical Z₃.normalize Z₃.normalize-canonical
    Z₃.canonical-is-fixed-Z3 Z₃.normalize-distrib
  -- Cycle component: FreeCyclic-Coxeter.
  (F.Word F.Gen) (F._++_) F.ε F.++-assoc
    F.Canonical F.normalize F.normalize-canonical
    F.canonical-is-fixed-Free F.normalize-distrib
  public

------------------------------------------------------------------------
-- After this slice:
--
--   * Word = Z₃.Word × F.Word  (= phase-word × cycle-word)
--   * _·_ : pair the products componentwise (phase mod 3, cycle as ℕ)
--   * normalize : pair the normalizations
--   * Canonical : both components canonical
--   * All Core lemmas inherited: normalize-idem, normalize-append,
--     normalize-distrib, clash, etc.
--
-- The Z₃ × FreeCyclic word `(phase, cycle)` represents the integer
-- `cycle * 3 + phase-as-ℕ` in the universal cover ℕ → Z/3. The phase
-- projection (slice 4) discards `cycle`; the cycle projection
-- extracts `cycle` from the pair.
------------------------------------------------------------------------
