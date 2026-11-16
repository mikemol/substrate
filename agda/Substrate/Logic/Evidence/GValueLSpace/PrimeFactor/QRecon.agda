------------------------------------------------------------------------
-- Substrate.Logic.Evidence.GValueLSpace.PrimeFactor.QRecon
--
-- Defines: q-recon
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.Logic.Evidence.GValueLSpace.PrimeFactor; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Logic.Evidence.GValueLSpace.PrimeFactor.QRecon where

open import Substrate.Foundation.Nat.Nat
open import Substrate.Foundation.List
open import Substrate.Algebra.Q.Rat
open import Substrate.Algebra.Z.Int
open import Substrate.Algebra.Nat.Prime
open import Substrate.Foundation.Eq
open import Substrate.Foundation.Eq.Cong
open import Substrate.Foundation.Eq.Cong2
open import Substrate.Logic.Evidence.GValueLSpace.PrimeFactor.Pred



-- Reconstruct a positive rational from its SIGNED prime factorisation:
--   nf = numerator primes (+exponents),  df = denominator primes (−exponents).
-- (den = suc (pred (product df)); on factorisation outputs product df ≥ 1 so
-- this is exact, and total elsewhere — pred floors the degenerate product 0.)
q-recon : List ℕ → List ℕ → ℚ
q-recon nf df = mkℚ (+ product nf) (pred (product df))
