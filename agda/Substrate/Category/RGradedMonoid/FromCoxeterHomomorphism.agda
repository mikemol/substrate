------------------------------------------------------------------------
-- Substrate.Category.RGradedMonoid.FromCoxeterHomomorphism
--
-- Combinator: any Coxeter Word algebra + an ℕ-valued monoid
-- homomorphism gives an F₂-graded RGradedMonoid via parity ∘ hom.
--
-- Consolidates the pattern shared by V4-F2Graded (length-parity),
-- V4-F2Graded-CountA (count-A-parity), V4-F2Graded-CountB (count-B-
-- parity), and any future F₂-graded Coxeter instance.
--
-- The chain that's being abstracted:
--   1. Have a Word A monoid (= some Coxeter Word).
--   2. Have an ℕ-homomorphism hom : Word A → ℕ (length, count-of-A,
--      count-of-B, weight, etc.).
--   3. The F₂-grading is parity ∘ hom; degree-· follows from
--      hom-distrib (= the homomorphism property of hom) + parity-+.
--
-- This combinator takes (Word, _++_, ε, monoid laws, hom, hom-laws)
-- and produces the F₂-graded RGradedMonoid record. Each F₂-graded
-- Coxeter instance becomes a one-line application.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

open import Data.Nat using (ℕ; _+_)
open import Relation.Binary.PropositionalEquality
  using (_≡_; refl; trans; cong)

module Substrate.Category.RGradedMonoid.FromCoxeterHomomorphism
  (Word : Set)
  (_++_ : Word → Word → Word)
  (ε : Word)
  (++-assoc      : (a b c : Word) → (a ++ b) ++ c ≡ a ++ (b ++ c))
  (++-identityˡ  : (a : Word) → ε ++ a ≡ a)
  (++-identityʳ  : (a : Word) → a ++ ε ≡ a)
  (hom           : Word → ℕ)
  (hom-ε         : hom ε ≡ 0)
  (hom-distrib   : (a b : Word) → hom (a ++ b) ≡ hom a + hom b)
  where

open import Substrate.Algebra.N-to-F2-Parity using (parity; parity-+)
open import Substrate.Algebra.F2-CommutativeMonoid using (F₂-CommMonoid)
open import Substrate.Category.RGradedMonoid

------------------------------------------------------------------------
-- The F₂-graded RGradedMonoid produced by the combinator.
--
-- degree = parity ∘ hom.
-- degree-ε = parity 0 ≡ 0 (refl).
-- degree-· = parity (hom (a ++ b))
--          ≡ parity (hom a + hom b)              [cong parity hom-distrib]
--          ≡ parity (hom a) + parity (hom b)      [parity-+]
------------------------------------------------------------------------

F₂Graded-from-Homomorphism : RGradedMonoid F₂-CommMonoid _
F₂Graded-from-Homomorphism = record
  { M           = Word
  ; _·_         = _++_
  ; ε           = ε
  ; ·-assoc     = ++-assoc
  ; ·-identityˡ = ++-identityˡ
  ; ·-identityʳ = ++-identityʳ
  ; degree      = λ w → parity (hom w)
  ; degree-ε    = trans (cong parity hom-ε) refl
  ; degree-·    = λ a b →
      trans (cong parity (hom-distrib a b))
            (parity-+ (hom a) (hom b))
  }

------------------------------------------------------------------------
-- Capstone.
--
-- After opening this module with a (Word, ++, ε, monoid-laws, hom,
-- hom-laws) tuple, the F₂-graded RGradedMonoid is available. Each
-- per-instance F₂-graded module becomes a one-line application.
--
-- Examples (downstream usage):
--   * V4-F2Graded (length-parity): hom = length, hom-distrib =
--     length-distrib. One-line wrapper.
--   * V4-F2Graded-CountA: hom = count-A, hom-distrib = count-A-distrib.
--   * V4-F2Graded-CountB: hom = count-B, hom-distrib = count-B-distrib.
--   * Future: count-of-X parities at any Coxeter instance.
------------------------------------------------------------------------
