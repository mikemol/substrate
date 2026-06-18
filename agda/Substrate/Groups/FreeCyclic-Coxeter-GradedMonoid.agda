------------------------------------------------------------------------
-- Substrate.Groups.FreeCyclic-Coxeter-GradedMonoid
--
-- FreeCyclic-Coxeter packaged as a GradedMonoid. The grading is by
-- length (= the canonical ℕ-grading on the free monoid on one
-- generator).
--
-- Establishes:
--   * degree-ε  : length [] ≡ 0
--   * degree-·  : length (a ++ b) ≡ length a + length b
--
-- The first is refl; the second by induction on the first word.
--
-- This is the canonical instance demonstrating that FreeCyclic IS
-- ℕ-as-a-monoid via the length bijection (slice 2 of the previous
-- arc) lifted to the categorical GradedMonoid record.
--
-- Per [[project-graded-bicategorical-arc]]: FreeCyclic's length is
-- THE substrate's degree function. This module makes the grading
-- structural at the category-primitive level.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Groups.FreeCyclic-Coxeter-GradedMonoid where

open import Substrate.Foundation.Nat using (ℕ; zero; suc; _+_)
open import Substrate.Foundation.Eq
  using (_≡_; refl; cong)

import Substrate.Groups.FreeCyclic-Coxeter as F
import Substrate.Groups.FreeCyclic-Coxeter-Length as F-Len
open import Substrate.Groups.Coxeter.Word
  using (Word; []; _∷_; _++_; ++-identity-left; ++-identity-right)
open import Substrate.Category.GradedMonoid

------------------------------------------------------------------------
-- N-1: The degree homomorphism.
--
-- length-of-word distributes over ++:
--   length (a ++ b) ≡ length a + length b
-- Proof by induction on a.
------------------------------------------------------------------------

length-distrib :
  (a b : Word F.Gen) →
  F-Len.length-of-word (a ++ b) ≡ F-Len.length-of-word a + F-Len.length-of-word b
length-distrib []      b = refl
length-distrib (x ∷ a) b = cong suc (length-distrib a b)

------------------------------------------------------------------------
-- N-2: FreeCyclic as GradedMonoid.
------------------------------------------------------------------------

FreeCyclic-GradedMonoid : GradedMonoid _
FreeCyclic-GradedMonoid = record
  { M           = Word F.Gen
  ; _·_         = _++_
  ; ε           = []
  ; ·-assoc     = λ a b c → F.++-assoc a b c
  ; ·-identityˡ = ++-identity-left
  ; ·-identityʳ = ++-identity-right
  ; degree      = F-Len.length-of-word
  ; degree-ε    = refl
  ; degree-·    = length-distrib
  }

------------------------------------------------------------------------
-- N-3: Capstone.
--
-- After this slice, FreeCyclic-Coxeter is available as the
-- canonical GradedMonoid instance — the substrate's "ℕ-as-monoid"
-- with explicit degree structure.
--
-- The degree homomorphism length-distrib is the structural witness
-- that ++ adds the lengths of the operands; length is a degree
-- HOMOMORPHISM here. Combined with the length bijection (proved in
-- FreeCyclic-Coxeter-Length, not here) it is faithful — that
-- injectivity is NOT proved in this module.
--
-- Per [[project-graded-bicategorical-arc]]: the next slices use
-- FreeCyclic-GradedMonoid as the "grading axis" of more complex
-- graded structures (Z_n-x-FreeCyclic gets a ℕ-grading on Z_n; etc.).
------------------------------------------------------------------------
