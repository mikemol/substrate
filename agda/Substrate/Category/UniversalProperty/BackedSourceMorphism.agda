{-# OPTIONS --safe --without-K #-}

------------------------------------------------------------------------
-- Substrate.Category.UniversalProperty.BackedSourceMorphism — ⟡backed-source-morphism:
-- a GENUINE Source-CHANGING BackedMorphism (σ ≠ id). Every prior BackedMorphism (178)
-- had σ = id (shared-Source fold reads). Here σ changes the Source TYPE.
--
-- GROUNDED (not invented): eq-backed's arrow eq-UP has Source = Target = ℕ, solve = id
-- (the equality UP, s solved by s). count-backed's Target = ℕ = eq-backed's Source. So
-- count-backed ⇒ eq-backed with σ = count-solve : SomeTraceℕ → ℕ (the Source CHANGES
-- from traces to ℕ), φ = id, and the square commutes by refl (solve eq-backed = id):
--   φ (count-solve s) ≡ solve eq-backed (σ s)  ⟺  count-solve s ≡ count-solve s.
-- This is a real Source-changing arrow between two REGISTERED solvers, and it COMPOSES
-- (via comp-backed) with the σ=id shape⇒count — showing the category mixes both.
------------------------------------------------------------------------

module Substrate.Category.UniversalProperty.BackedSourceMorphism where

open import Substrate.Foundation.Eq using (_≡_; refl)
open import Substrate.Foundation.Nat using (ℕ)
open import Substrate.Foundation.Product using (_,_)
open import Substrate.Category.UniversalProperty using (Source; Target)
open import Substrate.Category.UniversalProperty.Backed using (BackedUP; arrow; solve; eq-backed)
open import Substrate.Category.UniversalProperty.BackedTransport
  using (BackedMorphism; count-backed; count-solve; shape⇒count)
open import Substrate.Category.UniversalProperty.FoldRegistry using (shape-backed)
open import Substrate.Category.UniversalProperty.BackedCategory using (comp-backed)

------------------------------------------------------------------------
-- ① THE Source-CHANGING morphism count-backed ⇒ eq-backed. σ = count-solve (SomeTraceℕ
-- → ℕ, a genuine type change), φ = id (ℕ → ℕ), square = refl (solve eq-backed = id).
------------------------------------------------------------------------
count⇒eq : BackedMorphism count-backed eq-backed
count⇒eq =
    count-solve                       -- σ : SomeTraceℕ → ℕ  (the Source CHANGES)
  , (λ n → n)                          -- φ : ℕ → ℕ  (identity on the target)
  , (λ s → refl)                       -- square: count-solve s ≡ solve eq-backed (count-solve s)

------------------------------------------------------------------------
-- ② IT COMPOSES with the σ=id shape⇒count (178): shape-backed ⇒ count-backed ⇒ eq-backed.
-- The composite has σ = count-solve ∘ id = count-solve : SomeTraceℕ → ℕ (still Source-
-- changing), φ = id ∘ length = length. So the category genuinely mixes σ=id and σ≠id arrows.
------------------------------------------------------------------------
shape⇒eq : BackedMorphism shape-backed eq-backed
shape⇒eq = comp-backed {shape-backed} {count-backed} {eq-backed} shape⇒count count⇒eq

------------------------------------------------------------------------
-- THE INVARIANT (bottoming out — the arrows are not all σ=id): a BackedMorphism's σ can
-- genuinely CHANGE the Source type — count⇒eq maps traces (SomeTraceℕ) to ℕ via the
-- count-solve itself, landing in eq-backed (the equality solver, solve = id) where the
-- square is refl. This is grounded in REGISTERED solvers (count-backed, eq-backed), not
-- invented, and COMPOSES with the σ=id fold-transport arrows (shape⇒count) to give
-- shape⇒eq. So the category of registered solvers (181) has BOTH σ=id arrows (fold reads
-- of a shared Source) AND σ≠id arrows (Source-changing, e.g. a solver feeding its output
-- as another's problem). The "same-Source reads vs Source-changing maps" either/or
-- dissolves: both are BackedMorphisms (the solve-square), composed by the SAME comp-backed;
-- the category is closed under both. eq-backed acts as a receiver: any solver whose Target
-- is ℕ feeds eq-backed via σ = its own solve, φ = id — the solve becomes the Source-map.
------------------------------------------------------------------------
