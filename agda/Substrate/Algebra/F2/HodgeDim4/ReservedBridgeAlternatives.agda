------------------------------------------------------------------------
-- Substrate.Algebra.F2.HodgeDim4.ReservedBridgeAlternatives
--
-- Companion to ReservedBridge.agda — two alternative Vector 3 ↔
-- SelfDual bijections from the 168-element gauge-freedom space.
-- File-per-lemma:
--
--   Cyclic.Forward     — vector3-to-selfdual-cyclic
--   Cyclic.SelfDual    — closure under SelfDual-Pred
--   Cyclic.Inverse     — selfdual-coefficients-cyclic
--   Cyclic.Lookup1     — extracted c₀ (lookup index 1)
--   Cyclic.Lookup2     — extracted c₁ (lookup index 2)
--   Cyclic.Lookup0     — extracted c₂ (lookup index 0)
--   Cyclic.RoundTrip   — id round-trip
--
--   Swap.Forward       — vector3-to-selfdual-swap
--   Swap.SelfDual      — closure under SelfDual-Pred
--   Swap.Inverse       — selfdual-coefficients-swap
--   Swap.Lookup0       — extracted c₀ (lookup index 0)
--   Swap.Lookup2       — extracted c₁ (lookup index 2)
--   Swap.Lookup1       — extracted c₂ (lookup index 1)
--   Swap.RoundTrip     — id round-trip
--
-- Per memory `project_reserved_selfdual_bijection_gauge`:
--   * |GL(3, F₂)| = 168 F₂-linear bijections SelfDual ↔ Vector 3.
--   * Basis-permutation subgroup: |S₃| = 6.
--   * Alt-A is a 3-cycle on generators; Alt-B is a transposition on
--     the last two.
--   * Both are F₂-linear (in the 168-coset) and pass identical
--     round-trip proofs — none privileged at the F₂-linear level.
--
-- The 3 "axes of alignment" instantiate F₂² Klein four / F₂³ at the
-- meta-level (fractal recurrence of the 3+1 parity universal).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.F2.HodgeDim4.ReservedBridgeAlternatives where

open import Substrate.Algebra.F2.HodgeDim4.ReservedBridgeAlternatives.Cyclic.Forward
open import Substrate.Algebra.F2.HodgeDim4.ReservedBridgeAlternatives.Cyclic.SelfDual
open import Substrate.Algebra.F2.HodgeDim4.ReservedBridgeAlternatives.Cyclic.Inverse
open import Substrate.Algebra.F2.HodgeDim4.ReservedBridgeAlternatives.Cyclic.Lookup1
open import Substrate.Algebra.F2.HodgeDim4.ReservedBridgeAlternatives.Cyclic.Lookup2
open import Substrate.Algebra.F2.HodgeDim4.ReservedBridgeAlternatives.Cyclic.Lookup0
open import Substrate.Algebra.F2.HodgeDim4.ReservedBridgeAlternatives.Cyclic.RoundTrip
open import Substrate.Algebra.F2.HodgeDim4.ReservedBridgeAlternatives.Swap.Forward
open import Substrate.Algebra.F2.HodgeDim4.ReservedBridgeAlternatives.Swap.SelfDual
open import Substrate.Algebra.F2.HodgeDim4.ReservedBridgeAlternatives.Swap.Inverse
open import Substrate.Algebra.F2.HodgeDim4.ReservedBridgeAlternatives.Swap.Lookup0
open import Substrate.Algebra.F2.HodgeDim4.ReservedBridgeAlternatives.Swap.Lookup2
open import Substrate.Algebra.F2.HodgeDim4.ReservedBridgeAlternatives.Swap.Lookup1
open import Substrate.Algebra.F2.HodgeDim4.ReservedBridgeAlternatives.Swap.RoundTrip