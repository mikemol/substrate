------------------------------------------------------------------------
-- Substrate.Category.Allegory.Refinement.Chain
--
-- Defines: chain
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.Category.Allegory.Refinement; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Category.Allegory.Refinement.Chain where

open import Substrate.Foundation.Nat.Nat
open import Substrate.Foundation.Eq.Sym
open import Substrate.Foundation.Eq.Trans
open import Substrate.Foundation.Eq.Cong2
open import Substrate.Category.Allegory.Refinement.Preamble
open import Substrate.Category.Allegory.Refinement.SqsubF
open import Substrate.Category.Allegory.Refinement.Refinement
open import Substrate.Category.Allegory.Refinement.Iterate
open import Substrate.Algebra.F2.AES.KAT.Pre



-- from a pre-fixed-point Φ R⁰ ⊑ R⁰, the iterate is a DESCENDING chain
-- (inhabitants only shrink): Rⁿ⁺¹ ⊑ Rⁿ. The grade n = how far Φ has pruned.
chain : {A : Set} {Φ : (A → Set) → A → Set}
        {mono : {P Q : A → Set} → P ⊑ᶠ Q → Φ P ⊑ᶠ Φ Q}
        (Φr : Refinement A Φ mono) {R⁰ : A → Set}
      → (Φ R⁰ ⊑ᶠ R⁰) → (n : ℕ) → iterate Φr (suc n) R⁰ ⊑ᶠ iterate Φr n R⁰
chain                Φr pre zero    = pre
chain {mono = mono} Φr pre (suc n) = mono (chain Φr pre n)
