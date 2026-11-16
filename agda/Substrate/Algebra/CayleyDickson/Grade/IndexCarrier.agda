------------------------------------------------------------------------
-- The length-graded carrier at grade n IS popcount's domain — so popcount is a
-- SECOND ℕ-grading layered on the VecGraded length-grade, on the one carrier.
-- Context: Substrate/Algebra/CayleyDickson/Grade/README.md
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.CayleyDickson.Grade.IndexCarrier where

open import Substrate.Foundation.Bool.Bool
open import Substrate.Foundation.Nat.Nat
open import Substrate.Foundation.Iff.Iff
open import Substrate.Foundation.Iff.IffRefl
open import Substrate.Foundation.Vec

index-carrier : (n : ℕ) → Vec Bool n ⇔ Vec Bool n
index-carrier n = ⇔-refl
