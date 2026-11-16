------------------------------------------------------------------------
-- Substrate.Category.Allegory.Refinement.BWedge
--
-- Defines: BWedge
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.Category.Allegory.Refinement; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Category.Allegory.Refinement.BWedge where

open import Substrate.Foundation.Product
open import Substrate.Foundation.Nat.Lt
open import Substrate.Foundation.Nat.Nat
open import Substrate.Algebra.Wedge
open import Substrate.Foundation.Eq
open import Substrate.Foundation.Eq.Sym
open import Substrate.Foundation.Eq.Trans
open import Substrate.Foundation.Eq.Cong2
open import Substrate.Category.Allegory.Refinement.Preamble



------------------------------------------------------------------------
-- PART B — the concrete fusion: the bounded ℕ-wedge is a MAP.
------------------------------------------------------------------------

-- the bounded decomposition dividend ↦ (quotient, remainder), divisor (suc b).
BWedge : ℕ → ℕ → ℕ × ℕ → Set
BWedge b a qr = (proj₂ qr < suc b) × (a ≡ recon ℕ-div (proj₁ qr) (suc b) (proj₂ qr))
