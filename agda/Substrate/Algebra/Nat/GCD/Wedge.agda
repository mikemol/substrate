------------------------------------------------------------------------
-- Substrate.Algebra.Nat.GCD.Wedge
--
-- Wedge-GCD a b : modulo as a structural decomposition.
-- Packages (quotient, remainder, reconstruction equation, r < b).
-- Both the quotient AND remainder are essential structural data;
-- together they reconstruct `a`.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.Nat.GCD.Wedge where

open import Substrate.Foundation.Nat.Lt
open import Substrate.Foundation.Nat.Nat
open import Substrate.Foundation.Nat.Plus
open import Substrate.Foundation.Nat.Times
open import Substrate.Foundation.Eq

record Wedge-GCD (a b : ℕ) : Set where      -- ⟦shape:3014fd3e quotient,remainder,wedge-eq⟧
  field
    quotient  : ℕ
    remainder : ℕ
    wedge-eq  : a ≡ quotient * b ℕ+ remainder
    r<b       : remainder < b

open Wedge-GCD public
