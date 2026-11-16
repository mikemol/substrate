------------------------------------------------------------------------
-- Substrate.Algebra.Nat.Prime.Properties.FactorCanonical
--
-- Defines: factor-Canonical
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.Algebra.Nat.Prime.Properties; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.Nat.Prime.Properties.FactorCanonical where

open import Substrate.Foundation.Nat.Le
open import Substrate.Foundation.Nat.Nat
open import Substrate.Foundation.Product
open import Substrate.Foundation.List
open import Substrate.Algebra.Nat.DivMod.Unique.Private
open import Substrate.Algebra.Nat.WellFounded.Private
open import Substrate.Algebra.Quotient.Canonical
open import Substrate.Algebra.Quotient.KerQuotient
open import Substrate.Algebra.Quotient.SplitCanonical
open import Substrate.Algebra.Nat.Prime
open import Substrate.Foundation.Eq
open import Substrate.Foundation.Eq.Cong
open import Substrate.Algebra.Nat.Prime.Properties.FactorValue
open import Substrate.Algebra.Nat.Prime.Properties.FactorSection
open import Substrate.Algebra.Nat.Prime.Properties.FactorRetract



-- THE ISO: the split idempotent factor-section ∘ factor-value is a Canonical
-- for ker factor-value — ℕ⁺ ≅ canonical prime factorisations, from the
-- retraction alone (uniqueness/.u2 then characterises the image as THE multiset).
factor-Canonical : Canonical (ker-Quotient factor-value)
factor-Canonical = split-Canonical factor-value factor-section factor-retract
