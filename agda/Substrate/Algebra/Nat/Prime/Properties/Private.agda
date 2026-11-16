------------------------------------------------------------------------
-- Substrate.Algebra.Nat.Prime.Properties.Private
--
-- Defines: pred
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.Algebra.Nat.Prime.Properties; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.Nat.Prime.Properties.Private where

open import Substrate.Foundation.Nat.Le
open import Substrate.Foundation.Nat.Lt
open import Substrate.Foundation.Nat.Nat
open import Substrate.Foundation.Product
open import Substrate.Foundation.List
open import Substrate.Foundation.WellFounded
open import Substrate.Foundation.Nat.Properties.Mul.TimesComm
open import Substrate.Algebra.Nat.Divides.Type
open import Substrate.Algebra.Nat.WellFounded.LtWellFounded
open import Substrate.Algebra.Nat.WellFounded.Private
open import Substrate.Algebra.Nat.Prime
open import Substrate.Algebra.Nat.Prime.Properties.Factorize
open import Substrate.Foundation.Eq



------------------------------------------------------------------------
-- 8. Ⓝ.iso: the prime factorisation as a SPLIT-CANONICAL retraction.
--    `factorize!` gives product ∘ factorize ≡ id (the existence round-trip), a
--    retraction — so by the split-idempotent apex (`split-Canonical`) the
--    positive naturals ARE a section-based quotient: ℕ⁺ ≅ {canonical prime
--    factorisations} (the image of `factorize`), NO quotient type. (A positive
--    n is `suc m`; the carrier value is `pred (product ps)`, so the retraction
--    is total: pred (product (factorize (suc m))) = pred (suc m) = m.)
--    The same apex as eval/reify, ℚ reduce, the wedge recon (project_split_idempotent_apex).
------------------------------------------------------------------------

pred : ℕ → ℕ
pred zero    = zero
pred (suc n) = n
