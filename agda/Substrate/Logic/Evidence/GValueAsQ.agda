------------------------------------------------------------------------
-- Substrate.Logic.Evidence.GValueAsQ
--
-- Ω3: the el-atlas Nedge G-Value Calculus ↔ ℚ-Canonical.
--
-- el-atlas (nedge-decomposition.md) defines a G-VALUE as a positive scalar
-- G(P) ∈ (0,∞), with balance point G = 1 (Nedge's L = 0) and the ANTIPODE
-- CONSTRAINT  G(P) · G(¬P) = 1  (a balance channel: G = E⁺/E⁻, and ¬P swaps
-- the rails). The Drive Agda spec `NedgeGCalculus` POSTULATES this scalar and
-- proves no law in Agda (OB-6 / spec line-1987; see Verdict.NedgeShadow).
--
-- Here it is DERIVED, not postulated — the same discipline ℚ-Canonical is for
-- a number system (NedgeShadow's own pointer). A G-value is a POSITIVE ℚ
-- (suc na')/(suc db); balance is 1ℚ; the antipode is the reciprocal (the
-- numerator/denominator swap, total because the value is positive — no
-- division-by-zero); and the antipode constraint G·G(¬P) ≈ 1 is exactly ℚ's
-- multiplicative-inverse law, which here reduces to ℕ-multiplication
-- commutativity. Machine-checked over the ℚ-setoid ≈ℚ (cross-multiplication;
-- the inverse laws are TRUE over ≈ℚ, syntactically false over raw ≡).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Logic.Evidence.GValueAsQ where

open import Substrate.Foundation.Nat using (ℕ; zero; suc; _*_)
open import Substrate.Foundation.Nat.Properties.Mul using (*-comm)
open import Substrate.Foundation.Eq using (_≡_; refl; trans; sym; cong)
open import Substrate.Algebra.Z using (ℤ; +_; 1ℤ)
open import Substrate.Algebra.Z.Mul using (_*ℤ_)
open import Substrate.Algebra.Z.Properties.MulFull using (*ℤ-identityˡ; *ℤ-identityʳ)
open import Substrate.Algebra.Q using (ℚ; mkℚ; 1ℚ)
open import Substrate.Algebra.Q.Mul using (_*ℚ_)
open import Substrate.Algebra.Q.Equiv using (_≈ℚ_)

------------------------------------------------------------------------
-- A G-value: a POSITIVE rational scalar (suc na')/(suc db) ∈ (0,∞).
------------------------------------------------------------------------

gvalue : ℕ → ℕ → ℚ
gvalue na' db = mkℚ (+ suc na') db

-- balance point G = 1 (Nedge's L = 0).
balance : ℚ
balance = gvalue 0 0

balance-is-1ℚ : balance ≡ 1ℚ
balance-is-1ℚ = refl

-- the antipode G(¬P): the reciprocal (num/den swap) — total, since G is positive.
antipode-of : ℕ → ℕ → ℚ
antipode-of na' db = gvalue db na'

------------------------------------------------------------------------
-- THE G-VALUE LAW, DERIVED: G(P) · G(¬P) ≈ 1.  NedgeGCalculus postulates this;
-- here it is ℚ's multiplicative inverse, reduced to ℕ *-comm. Not a postulate.
------------------------------------------------------------------------

gvalue-antipode : (na' db : ℕ) → (gvalue na' db *ℚ antipode-of na' db) ≈ℚ 1ℚ
gvalue-antipode na' db =
  trans (*ℤ-identityʳ (+ (suc na' * suc db)))
  (trans (cong +_ (*-comm (suc na') (suc db)))
         (sym (*ℤ-identityˡ (+ (suc db * suc na')))))
