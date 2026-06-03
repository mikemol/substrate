------------------------------------------------------------------------
-- Substrate.Algebra.Z.Bezout.Examples
--
-- Oracle checks for the Bézout bridge fold, computed against the
-- typechecker (no aesthetic): gcd values by refl, and the bridge
-- s·a + t·b ≡ g held by construction of bezout-ℤ.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.Z.Bezout.Examples where

open import Substrate.Foundation.Eq using (_≡_; refl)
open import Substrate.Foundation.Product using (proj₁; proj₂)
open import Substrate.Algebra.Nat.GCD.ComputeTrace using (compute-trace)
open import Substrate.Algebra.Nat.GCD.Fold using (gcd-fold)
open import Substrate.Algebra.Z.Bezout using (BezoutℤWitness; bezout-ℤ)

-- gcd(12,8) = 4 (the trace index); the forgetful fold recovers it.
gcd-12-8       : proj₁ (compute-trace 12 8) ≡ 4
gcd-12-8       = refl
gcd-fold-12-8  : gcd-fold (proj₂ (compute-trace 12 8)) ≡ 4
gcd-fold-12-8  = refl

-- the WEDGE fold returns the bridge: constructing it typechecks the
-- carried equation s·12 + t·8 ≡ 4.
bezout-12-8 : BezoutℤWitness 12 8 (proj₁ (compute-trace 12 8))
bezout-12-8 = bezout-ℤ (proj₂ (compute-trace 12 8))

-- coprime: gcd(5,3) = 1, with a bridge s·5 + t·3 ≡ 1.
gcd-5-3     : proj₁ (compute-trace 5 3) ≡ 1
gcd-5-3     = refl
bezout-5-3  : BezoutℤWitness 5 3 (proj₁ (compute-trace 5 3))
bezout-5-3  = bezout-ℤ (proj₂ (compute-trace 5 3))
