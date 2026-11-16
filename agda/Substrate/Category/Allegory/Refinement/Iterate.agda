------------------------------------------------------------------------
-- Substrate.Category.Allegory.Refinement.Iterate
--
-- Defines: iterate
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.Category.Allegory.Refinement; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Category.Allegory.Refinement.Iterate where

open import Substrate.Foundation.Nat.Nat
open import Substrate.Foundation.Eq.Sym
open import Substrate.Foundation.Eq.Trans
open import Substrate.Foundation.Eq.Cong2
open import Substrate.Category.Allegory.Refinement.Preamble
open import Substrate.Category.Allegory.Refinement.SqsubF
open import Substrate.Category.Allegory.Refinement.Refinement



-- the stage-n iterate Rⁿ = Φⁿ R⁰.
iterate : {A : Set} {Φ : (A → Set) → A → Set}
          {mono : {P Q : A → Set} → P ⊑ᶠ Q → Φ P ⊑ᶠ Φ Q}
        → Refinement A Φ mono → ℕ → (A → Set) → A → Set
iterate         Φr zero    R⁰ = R⁰
iterate {Φ = Φ} Φr (suc n) R⁰ = Φ (iterate Φr n R⁰)
