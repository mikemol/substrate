------------------------------------------------------------------------
-- Substrate.Algebra.F2.Polynomial.Wedge.Inverse  (the GF(2⁸) inverse law)
--
-- THE KEYSTONE: every nonzero byte a has a multiplicative inverse modulo the
-- AES modulus m = x^8+x^4+x^3+x+1, with `a *Q a⁻¹ ≡ 𝟙` fully verified.
-- Composes the three landed pieces:
--   fuel-bezout (B-COMPUTE)      — the EEA produces s, t, g with s·a + t·m = g
--   g-unit-nth0/nths (B-INV-UNIT)— g is the unit (irreducibility, by reflection)
--   inverse-from-bezout (B-INV)  — s·a + t·m = 𝟙 ⇒ a · reduce s ≡ 𝟙
-- All instances align definitionally at (d=7, f-lo=m-lo): divisor-q's b-poly IS
-- ModZero's b-poly, and convCoeff/nth are instance-free (FromCommRing F₂).
-- Fully --safe, zero postulates.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.F2.Polynomial.Wedge.Inverse where

open import Substrate.Foundation.Nat using (ℕ; zero; suc)
open import Substrate.Foundation.Vec using (Vec; []; _∷_)
open import Substrate.Foundation.Product using (Σ; _,_; proj₁; proj₂)
open import Substrate.Foundation.Eq using (_≡_; refl)
open import Substrate.Foundation.Bool using (Bool; false)
import Substrate.Algebra.F2 as F2
open import Substrate.Algebra.F2.CommRing using (F₂-CommRing)
open import Substrate.Algebra.F2.Polynomial.Wedge.EEATrace using (QPoly; divisor-q)
open import Substrate.Algebra.F2.Polynomial.Wedge.FuelEEA using (fuel-bezout)
open import Substrate.Algebra.F2.Polynomial.Wedge.BezoutFold using (BezoutNthWitness)
open import Substrate.Algebra.F2.Polynomial.Wedge.GUnit
  using (m-lo; is-zero8; gcd-of; g-unit-nth0; g-unit-nths)
import Substrate.Algebra.Polynomial.Graded.ModZero as MZ
import Substrate.Algebra.Polynomial.Graded.FromCommRing as F
import Substrate.Algebra.Polynomial.Graded.Mod as GMod
import Substrate.Algebra.Polynomial.Graded.Quotient as Q
import Substrate.Algebra.Polynomial.Graded.Div as D
open F.Over F₂-CommRing using (Poly)
open GMod.Over F₂-CommRing 7 m-lo using (reduce-mod-f; oneC)
open Q.Over F₂-CommRing 7 m-lo using (_*Q_)

module M = MZ.Over F₂-CommRing 7 m-lo

-- the fuel-EEA Bézout run for a byte (fuel 10 ≥ 8 EEA steps).
W : (a : Poly 8) → Σ QPoly (BezoutNthWitness (8 , a) (divisor-q 7 m-lo))
W a = fuel-bezout 10 (8 , a) 7 m-lo

-- a⁻¹ = reduce (the Bézout cofactor s).
inv : Poly 8 → Poly 8
inv a = reduce-mod-f (proj₂ (proj₁ (proj₂ (W a))))

-- THE GF(2⁸) INVERSE LAW: every nonzero byte a has a · a⁻¹ ≡ 𝟙.
inv-law : (a : Poly 8) → is-zero8 a ≡ false → a *Q (inv a) ≡ oneC
inv-law a z = M.inverse-from-bezout
  (proj₂ (proj₁ (proj₂ (W a))))              -- s
  a                                          -- a
  (proj₂ (proj₁ (proj₂ (proj₂ (W a)))))      -- t
  (proj₂ (proj₁ (W a)))                      -- g
  (proj₂ (proj₂ (proj₂ (W a))))              -- bez : convCoeff s a + convCoeff t b-poly ≡ nth g
  (g-unit-nth0 a z)                          -- nth g 0 ≡ 𝟙
  (g-unit-nths a z)                          -- ∀k nth g (suc k) ≡ 𝟘
