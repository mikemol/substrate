------------------------------------------------------------------------
-- The bit indicator — the single source is Foundation.Bool.boolToℕ (⟡A4); this
-- names it at the grading's own vocabulary.
-- Context: Substrate/Algebra/CayleyDickson/Grade/README.md
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.CayleyDickson.Grade.Bit where

open import Substrate.Foundation.Bool.Bool
open import Substrate.Foundation.Nat.Nat
open import Substrate.Foundation.Bool.BoolToNat

bit : Bool → ℕ
bit = boolToℕ
