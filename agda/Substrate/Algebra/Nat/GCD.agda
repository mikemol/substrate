------------------------------------------------------------------------
-- Substrate.Algebra.Nat.GCD
--
-- Substrate-native ℕ-level Greatest Common Divisor + Least Common
-- Multiple via the Wedge + EEATrace technique. File-per-lemma:
--
--   GCD.Wedge             — modulo as a structural decomposition record.
--   GCD.ConstructWedge    — bridge to substrate's DivMod.
--   GCD.EEATrace          — Euclidean recursion as a data type.
--   GCD.ComputeTrace      — Acc-encapsulated trace construction.
--   GCD.GcdN              — extract gcd-ℕ from trace.
--   GCD.TraceDivides      — mutually-recursive trace-divides-{left,right}.
--   GCD.GcdDividesLeft    — gcd-ℕ a b ∣ a.
--   GCD.GcdDividesRight   — gcd-ℕ a b ∣ b.
--   GCD.LcmN              — loose-bound lcm-ℕ a b = a * b.
--   GCD.ADividesLcm       — a ∣ lcm-ℕ a b.
--   GCD.BDividesLcm       — b ∣ lcm-ℕ a b.
--
-- Stdlib audit: NO Data.Nat.Divisibility / Data.Nat.DivMod /
-- Data.Nat.Induction / Induction.WellFounded dependencies.
-- All ↑ are replaced by Substrate.Algebra.Nat.{Divides, DivMod,
-- WellFounded} + Substrate.Foundation.WellFounded.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.Nat.GCD where

open import Substrate.Algebra.Nat.GCD.Wedge
open import Substrate.Algebra.Nat.GCD.ConstructWedge
open import Substrate.Algebra.Nat.GCD.EEATrace
open import Substrate.Algebra.Nat.GCD.ComputeTrace
open import Substrate.Algebra.Nat.GCD.GcdN
open import Substrate.Algebra.Nat.GCD.TraceDivides
open import Substrate.Algebra.Nat.GCD.GcdDividesLeft
open import Substrate.Algebra.Nat.GCD.GcdDividesRight
open import Substrate.Algebra.Nat.GCD.LcmN
open import Substrate.Algebra.Nat.GCD.ADividesLcm
open import Substrate.Algebra.Nat.GCD.BDividesLcm