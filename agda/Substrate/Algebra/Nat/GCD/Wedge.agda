------------------------------------------------------------------------
-- Substrate.Algebra.Nat.GCD.Wedge
--
-- Wedge a b : modulo as a structural decomposition.
-- Packages (quotient, remainder, reconstruction equation, r < b).
-- Both the quotient AND remainder are essential structural data;
-- together they reconstruct `a`.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.Nat.GCD.Wedge where

open import Substrate.Foundation.Nat using (ℕ; _+_; _*_; _<_)
open import Substrate.Foundation.Eq using (_≡_)

record Wedge (a b : ℕ) : Set where      -- ⟦shape:b7e6a995 quotient,remainder,wedge-eq⟧
  field
    quotient  : ℕ
    remainder : ℕ
    wedge-eq  : a ≡ quotient * b + remainder
    r<b       : remainder < b

open Wedge public
