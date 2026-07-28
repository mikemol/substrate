------------------------------------------------------------------------
-- Substrate.Algebra.Lie.CartanA1  (Ⓛ — the shared A₁ Cartan type)
--
-- The Cartan type A₁ (rank 1; the 1×1 Cartan matrix m₀₀ = 1), factored out
-- of the L-arc's two concrete Lie algebras `sl2` (L14, Chevalley basis) and
-- `so3` (L15, angular-momentum basis), which each hand-rolled an identical
-- copy and asserted a "shared CartanType" in prose with no witness.
--
-- Now the sharing IS the witness: both `sl2-CartanType` and `so3-CartanType`
-- are DEFINITIONALLY this one `A1-CartanType` (not a propositional ≡ — the same
-- object). That is what "they share the A₁ Cartan type" means, made literal.
--
-- SCOPE — what the shared Cartan type does and does NOT say (the honest "not
-- only"): sl₂ and so₃ share the A₁ Cartan type = their COMPLEXIFICATIONS agree
-- (both complexify to sl₂(ℂ) = A₁). They are NOT isomorphic as REAL Lie
-- algebras — they are distinct real forms of A₁ (so₃ ≅ su(2), the COMPACT
-- form; sl₂(ℝ), the SPLIT form). A shared Cartan type is the complex
-- classification, not a real isomorphism; the earlier "so₃ ≅ sl₂(ℝ) as real
-- Lie algebras" was an overclaim. The real-form distinction is genuine and is
-- kept, not dissolved.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.Lie.CartanA1 where

open import Substrate.Category.CartanType using (CartanType; mkCartanType)
open import Substrate.Foundation.Eq using (_≡_; refl)
open import Substrate.Foundation.Fin.Fin
open import Substrate.Foundation.Nat using (ℕ)

-- A₁: rank 1, the 1×1 Cartan matrix is m₀₀ = 1.
A1-rank : ℕ
A1-rank = 1

A1-m : Fin A1-rank → Fin A1-rank → ℕ
A1-m _ _ = 1

A1-m-diag : (i : Fin A1-rank) → A1-m i i ≡ 1
A1-m-diag _ = refl

A1-m-symm : (i j : Fin A1-rank) → A1-m i j ≡ A1-m j i
A1-m-symm _ _ = refl

-- the A₁ Cartan type — the ONE object sl2-CartanType and so3-CartanType are.
A1-CartanType : CartanType
A1-CartanType = mkCartanType A1-rank A1-m A1-m-diag A1-m-symm
