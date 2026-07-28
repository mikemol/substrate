------------------------------------------------------------------------
-- Substrate.Category.Poly.Sites.FinPoly
--
-- Concrete site: polynomial functors at finite types.
--
-- For each n : ℕ, we have:
--   Positions  = Fin n       (n positions)
--   Directions = (i : Fin n) → Fin (arity i)    (variable arity)
--
-- This site instantiates the abstract Poly record at substrate-
-- native Fin types, demonstrating that polynomial functors can be
-- built with term-algebraic carriers.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Category.Poly.Sites.FinPoly where

open import Substrate.Foundation.Fin.Fin
open import Substrate.Foundation.Nat using (ℕ)

open import Substrate.Category.Poly

------------------------------------------------------------------------
-- A polynomial functor at Fin n positions with constant arity k.
--
-- (P y) = Σ (i : Fin n) → (Fin k → y)
-- I.e., for each position, k targets in y.

constant-arity-Fin-Poly : (n k : ℕ) → Poly (Fin n) (λ _ → Fin k)
constant-arity-Fin-Poly n k = record {}

------------------------------------------------------------------------
-- A polynomial functor with VARIABLE arity per position.
--
-- The arity is given by an arity function arity-fn : Fin n → ℕ.

variable-arity-Fin-Poly :
  (n : ℕ) (arity-fn : Fin n → ℕ) → Poly (Fin n) (λ i → Fin (arity-fn i))
variable-arity-Fin-Poly n arity-fn = record {}

------------------------------------------------------------------------
-- Per [[expose-generator-not-orbit]]: the polynomial functor's
-- (Positions, Directions) generators are exposed; concrete
-- polynomials are orbits.
--
-- Per the FieldFanOut generalization 2026-05-21: this site IS the
-- categorical view of FieldFanOut over Fin n with arity-fn. The
-- Substrate.Category.Poly.Connections module already shows the
-- correspondence.
