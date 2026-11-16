------------------------------------------------------------------------
-- Substrate.Algebra.Quotient.Surreal.Approx
--
-- Defines: _≈_
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.Algebra.Quotient.Surreal; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.Quotient.Surreal.Approx where

open import Substrate.Algebra.Quotient.Quotient
open import Substrate.Foundation.Nat.Nat
-- ⚑ Ⓑ4ᵃ: `SurrealFinite` and `≈ⁿ` were unbound — a split left this leaf without
-- the imports its body needs. Homes from `resolve_notinscope`, one each.
-- ⚑ ONLY `SurrealFinite` APPEARED IN THE BUILD LOG: scope checking stops at the
-- first failure, so `≈ⁿ` was invisible until that one was fixed. A log is a
-- record of what the compiler REACHED, never of what is missing — asking the
-- resolver for both names found the second before another build cycle did.
open import Substrate.Conway.SurrealFinite
open import Substrate.Conway.Equivalence




------------------------------------------------------------------------
-- 1. Homogeneous fixed-birthday ≈ⁿ.
------------------------------------------------------------------------

_≈_ : {n : ℕ} → SurrealFinite (suc n) → SurrealFinite (suc n) → Set
x ≈ y = x ≈ⁿ y
