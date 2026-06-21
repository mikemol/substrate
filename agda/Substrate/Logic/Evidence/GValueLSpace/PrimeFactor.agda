------------------------------------------------------------------------
-- Substrate.Logic.Evidence.GValueLSpace.PrimeFactor
--
-- Ⓝ.iso3 — the ℚ₊-signed exponent-difference. A positive rational
-- (suc na')/(suc db) is represented by its SIGNED prime factorisation:
-- numerator primes as +exponents, denominator primes as −exponents — the
-- ⊕primesℤ vector. This is the ℚ₊ lift of the ℕ⁺ factorisation iso
-- (Algebra.Nat.Prime), homed HERE in the Evidence layer (carrier-locality:
-- ℕ must not import ℚ), reusing `factor-section` + its round-trip.
--
-- The headline `q-factored-roundtrip`: every positive G-value reconstructs
-- EXACTLY from (factorise num, factorise den) — the representation is faithful
-- (the ℚ₊ ≅ ⊕primesℤ retraction direction).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Logic.Evidence.GValueLSpace.PrimeFactor where

open import Substrate.Foundation.Nat using (ℕ; zero; suc)
open import Substrate.Foundation.Eq using (_≡_; refl; cong; cong₂)
open import Substrate.Foundation.List using (List)
open import Substrate.Algebra.Q using (ℚ; mkℚ)
open import Substrate.Algebra.Z using (ℤ; +_)
open import Substrate.Algebra.Nat.Prime using (product)
open import Substrate.Algebra.Nat.Prime.Properties using (factor-section; factor-section-product)
open import Substrate.Logic.Evidence.GValueAsQ using (gvalue)

private
  pred : ℕ → ℕ
  pred zero    = zero
  pred (suc n) = n

-- Reconstruct a positive rational from its SIGNED prime factorisation:
--   nf = numerator primes (+exponents),  df = denominator primes (−exponents).
-- (den = suc (pred (product df)); on factorisation outputs product df ≥ 1 so
-- this is exact, and total elsewhere — pred floors the degenerate product 0.)
q-recon : List ℕ → List ℕ → ℚ
q-recon nf df = mkℚ (+ product nf) (pred (product df))

-- THE ℚ₊ ROUND-TRIP: every positive G-value reconstructs from (factorise num,
-- factorise den) — the signed exponent-difference representation is FAITHFUL.
-- Exact ≡ (not just ≈ℚ) via the two ℕ⁺ factorisation round-trips.
q-factored-roundtrip : (na' db : ℕ) →
  q-recon (factor-section na') (factor-section db) ≡ gvalue na' db
q-factored-roundtrip na' db =
  cong₂ (λ n d → mkℚ (+ n) d)
    (factor-section-product na')
    (cong pred (factor-section-product db))
