------------------------------------------------------------------------
-- Substrate.WitnessTower.Enumerate.Factorial
--
-- Defines: factorial
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.WitnessTower.Enumerate; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.WitnessTower.Enumerate.Factorial where

open import Substrate.Foundation.Nat.Nat
open import Substrate.Foundation.Nat.Times
open import Substrate.Foundation.Fin.Fin



------------------------------------------------------------------------
-- 4. The glue, proved: |perms (suc n)| = (suc n) · |perms n|, and the
--    running fold |perms n| = n!. (factorial as the catamorphism.)
------------------------------------------------------------------------

factorial : ℕ → ℕ
factorial zero    = suc zero
factorial (suc n) = suc n * factorial n
