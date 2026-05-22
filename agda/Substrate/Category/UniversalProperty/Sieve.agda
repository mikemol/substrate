------------------------------------------------------------------------
-- Substrate.Category.UniversalProperty.Sieve
--
-- UP13 of the UP-topos arc per [scratch/up_topos_arc_plan.md].
--
-- A SIEVE on a UPArrow U is a downward-closed family of UPTerms
-- into U: a subset S of the slice (UPCategory / U) closed under
-- precomposition.
--
-- Substrate-native: encoded as a predicate
--   S : {V : UPArrow} → UPTerm V U → Set
-- with the downward-closure axiom (S contains t implies S contains
-- t ∘ u for any precomposed u).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Category.UniversalProperty.Sieve where

open import Substrate.Category.UniversalProperty using (UPArrow)
open import Substrate.Category.UniversalProperty.Term
  using (UPTerm; _++ᵤ_)

------------------------------------------------------------------------
-- 1. The Sieve record.
--
-- A sieve at U is a family of predicates `member` indexed by source
-- UPArrow, closed under precomposition.
------------------------------------------------------------------------

record Sieve (U : UPArrow) : Set₂ where
  field
    member :
      {V : UPArrow} → UPTerm V U → Set₁
    closure :
      {V W : UPArrow}
      (t : UPTerm V U) (u : UPTerm W V) →
      member t →
      member (u ++ᵤ t)

open Sieve public

------------------------------------------------------------------------
-- 2. The maximal sieve (always-true predicate).
------------------------------------------------------------------------

record ⊤₁ : Set₁ where
  constructor tt₁

max-Sieve : (U : UPArrow) → Sieve U
max-Sieve U = record
  { member  = λ _ → ⊤₁
  ; closure = λ _ _ _ → tt₁
  }

------------------------------------------------------------------------
-- 3. Capstone for UP13.
--
-- Sieve + max-Sieve land. UP14 supplies cover-stable sieve closure;
-- UP15-UP16 the Grothendieck pretopology axioms.
------------------------------------------------------------------------
