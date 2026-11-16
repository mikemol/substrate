------------------------------------------------------------------------
-- Substrate.Logic.Evidence.GValueLSpace.PrimeFactor.QFactoredRoundtrip
--
-- Defines: q-factored-roundtrip
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.Logic.Evidence.GValueLSpace.PrimeFactor; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Logic.Evidence.GValueLSpace.PrimeFactor.QFactoredRoundtrip where

open import Substrate.Foundation.Nat.Nat
open import Substrate.Foundation.List
open import Substrate.Algebra.Q.Rat
open import Substrate.Algebra.Z.Int
open import Substrate.Algebra.Nat.Prime
open import Substrate.Algebra.Nat.Prime.Properties.DividesToLe
open import Substrate.Algebra.Nat.Prime.Properties.DividesTomod0
open import Substrate.Algebra.Nat.Prime.Properties.Dividessuc
open import Substrate.Algebra.Nat.Prime.Properties.FactorCanonical
open import Substrate.Algebra.Nat.Prime.Properties.FactorRetract
open import Substrate.Algebra.Nat.Prime.Properties.FactorSection
open import Substrate.Algebra.Nat.Prime.Properties.FactorSectionProduct
open import Substrate.Algebra.Nat.Prime.Properties.FactorValue
open import Substrate.Algebra.Nat.Prime.Properties.Factorize
open import Substrate.Algebra.Nat.Prime.Properties.Factorize2
open import Substrate.Algebra.Nat.Prime.Properties.LeToLtSumEq
open import Substrate.Algebra.Nat.Prime.Properties.Mod0ToDivides
open import Substrate.Algebra.Nat.Prime.Properties.PrimalityDecision
open import Substrate.Algebra.Nat.Prime.Properties.PrimeDividesProduct
open import Substrate.Algebra.Nat.Prime.Properties.PrimeDividesprimeToEq
open import Substrate.Algebra.Nat.Prime.Properties.PrimeDivisor
open import Substrate.Algebra.Nat.Prime.Properties.PrimeProduct
open import Substrate.Algebra.Nat.Prime.Properties.Private
open import Substrate.Algebra.Nat.Prime.Properties.Product
open import Substrate.Algebra.Nat.Prime.Properties.ProductAppend
open import Substrate.Algebra.Nat.Prime.Properties.QLtqTimesp
open import Substrate.Algebra.Nat.Prime.Properties.Search
open import Substrate.Algebra.Nat.Prime.Properties.StepCandidate
open import Substrate.Algebra.Nat.Prime.Properties.TwoDivides6
open import Substrate.Algebra.Nat.Prime.Properties.TwoLeToNotLt2
open import Substrate.Logic.Evidence.GValueAsQ
open import Substrate.Foundation.Eq
open import Substrate.Foundation.Eq.Cong
open import Substrate.Foundation.Eq.Cong2
open import Substrate.Logic.Evidence.GValueLSpace.PrimeFactor.Pred
open import Substrate.Logic.Evidence.GValueLSpace.PrimeFactor.QRecon



-- THE ℚ₊ ROUND-TRIP: every positive G-value reconstructs from (factorise num,
-- factorise den) — the signed exponent-difference representation is FAITHFUL.
-- Exact ≡ (not just ≈ℚ) via the two ℕ⁺ factorisation round-trips.
q-factored-roundtrip : (na' db : ℕ) →
  q-recon (factor-section na') (factor-section db) ≡ gvalue na' db
q-factored-roundtrip na' db =
  cong₂ (λ n d → mkℚ (+ n) d)
    (factor-section-product na')
    (cong pred (factor-section-product db))
