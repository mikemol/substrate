------------------------------------------------------------------------
-- Substrate.Algebra.Quotient.Quotient
--
-- Defines: Quotient
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.Algebra.Quotient; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.Quotient.Quotient where
open import Agda.Primitive



------------------------------------------------------------------------
-- 1. The base Quotient record: an equivalence relation, nothing more.
--
-- Surreals attach here directly via `_≈ⁿ_` from
-- Substrate.Conway.Equivalence.
------------------------------------------------------------------------

record Quotient {a r : Level} (A : Set a) (_≈_ : A → A → Set r) : Set (a ⊔ r) where
  field
    ≈-refl  : (a : A) → a ≈ a
    ≈-sym   : {a b : A} → a ≈ b → b ≈ a
    ≈-trans : {a b c : A} → a ≈ b → b ≈ c → a ≈ c

open Quotient public
