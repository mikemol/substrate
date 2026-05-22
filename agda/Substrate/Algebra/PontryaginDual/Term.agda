------------------------------------------------------------------------
-- Substrate.Algebra.PontryaginDual.Term (T21)
--
-- Term-algebra encoding of Pontryagin-dual characters via the
-- substrate's Coxeter Word infrastructure for cyclic groups.
--
-- For Z/n with cyclic generator g, characters are g^0, g^1, ..., g^(n-1).
-- Each character IS a Coxeter word on one generator; multiplication =
-- word concatenation modulo the cyclic relation g^n ≡ e.
--
-- Per [[roll-our-own-via-word-algebra]]: cyclic characters are
-- naturally word-algebraic.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.PontryaginDual.Term where

open import Substrate.Foundation.Nat using (ℕ)

-- A character of Z/n indexed by a power. The CharTerm IS the
-- power; concrete Coxeter-Word integration happens at use-site
-- via Substrate.Groups.Coxeter.FreeCyclic.

data CharGen (n : ℕ) : Set where
  gen-power : ℕ → CharGen n   -- g^k for k ∈ ℕ; reduce mod n at use-site

data CharTerm (n : ℕ) : Set where
  []  : CharTerm n
  _∷_ : CharGen n → CharTerm n → CharTerm n

infixr 5 _∷_

-- Character multiplication = term concatenation (= word multiplication
-- in the cyclic group's word algebra).

_++ᵪ_ : {n : ℕ} → CharTerm n → CharTerm n → CharTerm n
[]       ++ᵪ ys = ys
(x ∷ xs) ++ᵪ ys = x ∷ (xs ++ᵪ ys)

infixr 4 _++ᵪ_
