------------------------------------------------------------------------
-- Substrate.Algebra.Quotient.V4Cosets
--
-- QU7 of the QU-arc per [scratch/qu_arc_plan.md].
--
-- V₄-cosets in S₄ → base Quotient instance.
--
-- The equivalence `_∼V₄_ : Permutation → Permutation → Set` from
-- `Substrate.Groups.V4-Cosets` partitions S₄ into V₄-cosets, and
-- the substrate's existing ∼V₄-refl/sym/trans witnesses make
-- `Quotient Permutation _∼V₄_` immediate.
--
-- NO Canonical extension is attached. The substrate's
-- `coset-has-stab-rep` + `coset-stab-rep-unique` theorems give
-- "unique stab-rep up to ≈", not "unique stab-rep up to ≡". A
-- Canonical instance would require propositional equality on
-- Permutation, which needs funext (forbidden by the extraction
-- discipline). The base Quotient is structurally sufficient for
-- the UP factorisation property (per QU2's
-- `trivial-QuotientUP`).
--
-- Per [[homology-cohomology-recursion]]: this attachment is the
-- coset-pattern's promotion to internal structure. CY-5 (V₄ ⋊ S₃
-- ≅ S₄ with quotient ≅ S₃) becomes a Quotient instance, not a
-- bespoke proof.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.Quotient.V4Cosets where

open import Substrate.Groups.S4 using (Permutation)
open import Substrate.Groups.V4-Cosets
  using (_∼V₄_; ∼V₄-refl; ∼V₄-sym; ∼V₄-trans)

open import Substrate.Algebra.Quotient using (Quotient)

------------------------------------------------------------------------
-- 1. V₄-coset Quotient instance.
--
-- Bundles the substrate's existing ∼V₄ equivalence witnesses into
-- the substrate-native Quotient record. No Canonical extension —
-- see header.
------------------------------------------------------------------------

V4Cosets-Quotient : Quotient Permutation _∼V₄_
V4Cosets-Quotient = record
  { ≈-refl  = ∼V₄-refl
  ; ≈-sym   = λ {σ} {τ}   στ   → ∼V₄-sym   {σ} {τ}   στ
  ; ≈-trans = λ {σ} {τ} {ρ} στ τρ → ∼V₄-trans {σ} {τ} {ρ} στ τρ
  }

------------------------------------------------------------------------
-- 2. Capstone for QU7.
--
-- V₄-cosets attached as a base Quotient. The UP-factorisation
-- property goes through QU2's trivial-QuotientUP; downstream
-- cocycle-respecting maps out of S₄ now have a UP-witness.
------------------------------------------------------------------------
