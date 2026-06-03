------------------------------------------------------------------------
-- Substrate.Category.Coalgebra.StructuralGCD
--
-- The Euclid-algorithmic backbone for joint cyclic actions — DEFINITION
-- module. Names the substrate's structural primitive for commuting
-- finite-order endomaps:
--
--   Commute γ₁ γ₂   — pointwise commutativity
--
-- The proof-bearing results (commute-iterate-r, iterate-split-commute,
-- HasOrder-compose-commute) live in
-- Substrate.Category.Coalgebra.StructuralGCD.Properties, per the
-- def/proof separation policy (scratch/def_proof_separation_policy.md):
-- the proofs import Nat.Properties, and keeping that out of THIS module
-- means a consumer that only needs the `Commute` structure pays no
-- arithmetic-proof closure.
--
-- Per [[project-composite-torsion-euler-substrate]]: this is the
-- composite-torsion-via-commuting-factors lift. When γ₁ of order k₁
-- and γ₂ of order k₂ commute, their joint generates a cyclic
-- substructure whose order divides k₁ · k₂.
--
-- Per `feedback_categorical_name_first`: "Commute" is the categorical
-- name for commuting endomorphisms (an abelian subgroup of an
-- automorphism group).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Category.Coalgebra.StructuralGCD where

open import Substrate.Foundation.Level using (Level)
open import Substrate.Foundation.Eq using (_≡_; sym)

open import Substrate.Category.Coalgebra using (Endomap)

private
  variable
    ℓ : Level
    X : Set ℓ

------------------------------------------------------------------------
-- N-1: Commute — two endomaps commute pointwise.
--
-- Captures: γ₁ ∘E γ₂ ≡ γ₂ ∘E γ₁ at the function level (via pointwise
-- equality, avoiding funext).
--
-- An abelian subgroup of Aut(X) consists of pairwise-commuting
-- endomorphisms.
------------------------------------------------------------------------

record Commute {X : Set ℓ} (γ₁ γ₂ : Endomap X) : Set ℓ where
  field
    commute : (x : X) → γ₁ (γ₂ x) ≡ γ₂ (γ₁ x)

open Commute public

-- Commutativity is symmetric.  (Pure structural rearrangement of the
-- record; no arithmetic, so it stays in the definition module.)
commute-sym : {X : Set ℓ} {γ₁ γ₂ : Endomap X} →
              Commute γ₁ γ₂ → Commute γ₂ γ₁
commute-sym c = record { commute = λ x → sym (commute c x) }
