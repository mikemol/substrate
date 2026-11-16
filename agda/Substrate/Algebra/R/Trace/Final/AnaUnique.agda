------------------------------------------------------------------------
-- Substrate.Algebra.R.Trace.Final.AnaUnique
--
-- Defines: ana-unique
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.Algebra.R.Trace.Final; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K --guardedness #-}

module Substrate.Algebra.R.Trace.Final.AnaUnique where

open import Substrate.Foundation.Nat.Nat
open import Substrate.Foundation.Product
open import Substrate.Algebra.R.Trace
open import Substrate.Algebra.R.Trace.Unfold
open import Substrate.Algebra.R.Trace.Bisim.Cons
open import Substrate.Algebra.R.Trace.Bisim.Op
open import Substrate.Foundation.Eq
open import Substrate.Algebra.R.Trace.Final.Coalg
open import Substrate.Algebra.R.Trace.Final.Into
open import Substrate.Algebra.R.Trace.Final.Ana



------------------------------------------------------------------------
-- TERMINALITY (the universal property) — coinduction is its uniqueness clause.
-- Any h : S → RealTrace that is a coalgebra morphism (its head/tail match the
-- coalgebra c) is bisimilar to ana c. This is the generic "infinite behaviours
-- are universally dual": all morphisms into RealTrace agree up to `~`.
------------------------------------------------------------------------

-- The morphism's tail-square is only PROPOSITIONAL (tail (h s) ≡ h (proj₂ (c s))),
-- and transporting `~` along it under `tail~` would break guardedness. We instead
-- carry the witness `t ≡ h s` as a parameter and consume it `refl` inside the
-- copattern, so the corecursive call sits DIRECTLY under `tail~` (guarded).
ana-unique : {S : Set} (c : Coalg S) (h : S → RealTrace)
           → (∀ s → head (h s) ≡ proj₁ (c s))
           → (∀ s → tail (h s) ≡ h (proj₂ (c s)))
           → ∀ s → h s ~ ana c s
ana-unique {S} c h hh ht s₀ = go s₀ (h s₀) refl
  where
    go : (s : S) (t : RealTrace) → t ≡ h s → t ~ ana c s
    head~ (go s t refl) = hh s
    tail~ (go s t refl) = go (proj₂ (c s)) (tail t) (ht s)
