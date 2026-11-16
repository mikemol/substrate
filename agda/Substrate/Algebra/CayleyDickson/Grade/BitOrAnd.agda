------------------------------------------------------------------------
-- Inclusion-exclusion at one bit: |a∨b| ℕ+ |a∧b| = |a| ℕ+ |b|.
-- Context: Substrate/Algebra/CayleyDickson/Grade/README.md
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.CayleyDickson.Grade.BitOrAnd where

open import Substrate.Foundation.Bool.Bool
open import Substrate.Foundation.Nat.Nat
open import Substrate.Foundation.Nat.Plus
open import Substrate.Foundation.Bool.And
open import Substrate.Foundation.Bool.BoolToNat
open import Substrate.Foundation.Bool.Or
open import Substrate.Algebra.CayleyDickson.Grade.Bit
open import Substrate.Foundation.Eq

bit-or-and : (a b : Bool) → bit (a ∨ b) ℕ+ bit (a ∧ b) ≡ bit a ℕ+ bit b
bit-or-and true  true  = refl
bit-or-and true  false = refl
bit-or-and false true  = refl
bit-or-and false false = refl
