------------------------------------------------------------------------
-- Substrate.Groups.V4-Coxeter-F2Graded-CountB
--
-- V₄'s third F₂-grading: count of B generators, mod 2.
--
-- Mirror of count-A-parity (slice 16). Together with count-A-parity,
-- the pair (count-A-parity, count-B-parity) gives the V₄ ≅ Z/2 × Z/2
-- coordinate isomorphism as a pair of monoid homomorphisms into F₂.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Groups.V4-Coxeter-F2Graded-CountB where

open import Data.Nat using (ℕ; zero; suc; _+_)
open import Relation.Binary.PropositionalEquality
  using (_≡_; refl; cong; trans)

import Substrate.Groups.V4-Coxeter as V₄
open import Substrate.Groups.Coxeter.Word
  using (Word; []; _∷_; _++_; ++-identity-left; ++-identity-right)
open import Substrate.Algebra.N-to-F2-Parity using (parity; parity-+)
open import Substrate.Algebra.F2-CommutativeMonoid using (F₂-CommMonoid)
open import Substrate.Category.RGradedMonoid

------------------------------------------------------------------------
-- N-1: count-B — count of B generators.
------------------------------------------------------------------------

count-B : Word V₄.Gen → ℕ
count-B []          = zero
count-B (V₄.A ∷ w)  = count-B w
count-B (V₄.B ∷ w)  = suc (count-B w)

count-B-distrib :
  (a b : Word V₄.Gen) →
  count-B (a ++ b) ≡ count-B a + count-B b
count-B-distrib []          b = refl
count-B-distrib (V₄.A ∷ a)  b = count-B-distrib a b
count-B-distrib (V₄.B ∷ a)  b = cong suc (count-B-distrib a b)

------------------------------------------------------------------------
-- N-2: V₄ as F₂-graded by count-B-parity.
------------------------------------------------------------------------

V4-F2Graded-CountB : RGradedMonoid F₂-CommMonoid _
V4-F2Graded-CountB = record
  { M           = Word V₄.Gen
  ; _·_         = _++_
  ; ε           = []
  ; ·-assoc     = λ a b c → V₄.++-assoc a b c
  ; ·-identityˡ = ++-identity-left
  ; ·-identityʳ = ++-identity-right
  ; degree      = λ w → parity (count-B w)
  ; degree-ε    = refl
  ; degree-·    = λ a b →
      trans (cong parity (count-B-distrib a b))
            (parity-+ (count-B a) (count-B b))
  }

------------------------------------------------------------------------
-- N-3: Capstone — V₄'s three F₂-gradings complete.
--
-- Length-parity, count-A-parity, count-B-parity together give three
-- F₂-valued homomorphisms V₄ → F₂. The pair (count-A, count-B) is
-- a coordinate iso V₄ ≅ Z/2 × Z/2.
--
-- Length-parity is the SUM of count-A-parity and count-B-parity:
--   length = count-A + count-B (every generator is A or B)
--   length mod 2 = (count-A + count-B) mod 2
--                = (count-A mod 2) + (count-B mod 2)   [parity-+]
-- This is the structural relation between the three gradings.
------------------------------------------------------------------------
