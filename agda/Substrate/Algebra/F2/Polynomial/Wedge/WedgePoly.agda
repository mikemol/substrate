------------------------------------------------------------------------
-- Substrate.Algebra.F2.Polynomial.Wedge.WedgePoly
--
-- Wedge-Poly: polynomial division as structural decomposition.
-- Mirrors ℕ-level Wedge from Substrate.Algebra.Nat.GCD: captures
--   p = quotient *P q +P remainder, with degree remainder < degree q.
-- (Reconstruction equation deferred — requires mature *P length-arithmetic.)
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.F2.Polynomial.Wedge.WedgePoly where

open import Substrate.Foundation.Nat using (ℕ)
open import Substrate.Algebra.F2.Polynomial using (Polynomial)

record Wedge-Poly {n m : ℕ} (p : Polynomial n) (q : Polynomial m) : Set where
  field
    quotient-size  : ℕ
    quotient       : Polynomial quotient-size
    remainder-size : ℕ
    remainder      : Polynomial remainder-size

open Wedge-Poly public
