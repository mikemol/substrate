------------------------------------------------------------------------
-- Substrate.Groups.V4-Coxeter-F2Graded
--
-- V₄-Coxeter packaged as an F₂-graded monoid (= RGradedMonoid F₂-CommMonoid).
--
-- The grading: degree = parity of word length. Each V₄-Coxeter word
-- is either "even-length" (degree 𝟘 ∈ F₂) or "odd-length" (degree
-- 𝟙 ∈ F₂). The chirality element of V₄'s 3+1 parity universal IS
-- the odd-degree pole.
--
-- Per [[project-3plus1-as-graded-cocycle]]: V₄'s 3+1 parity = the
-- F₂-grading split. The 3 elements {A, B, AB} have specific parities:
--   * A      : length 1, parity 𝟙 (degree 1)
--   * B      : length 1, parity 𝟙 (degree 1)
--   * AB     : length 2, parity 𝟘 (degree 0)
--   * ε      : length 0, parity 𝟘 (degree 0)
-- So V₄ splits as {ε, AB} (degree 0, the "diagonal" subgroup) +
-- {A, B} (degree 1, the "off-diagonal").
--
-- Note: this is one of MULTIPLE possible F₂-gradings on V₄. The
-- "natural" 3+1 grading from project-3plus1-parity-universal might
-- use a different sense (V₄-Nonzero vs identity). The length-parity
-- grading IS structurally meaningful but not THE 3+1 split.
--
-- The 3+1 in V₄'s universal sense (3 nonzero + 1 identity) is at
-- the carrier-set level, not at the F₂-grading level. The
-- length-parity grading splits V₄ as 2+2 (even-length vs odd-length
-- elements). These are different decompositions of V₄.
--
-- Slice 16 will instantiate the "true" 3+1 grading as a separate
-- RGradedMonoid.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Groups.V4-Coxeter-F2Graded where

import Substrate.Groups.V4-Coxeter as V₄
open import Substrate.Groups.Coxeter.Word
  using (Word; []; _++_; ++-identity-left; ++-identity-right)
open import Substrate.Groups.Coxeter.Word.Length using (length; length-distrib)
open import Substrate.Algebra.N-to-F2-Parity using (parity; parity-+)
open import Substrate.Algebra.F2-CommutativeMonoid using (F₂-CommMonoid)
open import Substrate.Category.RGradedMonoid
open import Relation.Binary.PropositionalEquality
  using (_≡_; refl; trans; cong)

------------------------------------------------------------------------
-- N-1: V₄ as F₂-graded by length-parity.
------------------------------------------------------------------------

V4-F2Graded : RGradedMonoid F₂-CommMonoid _
V4-F2Graded = record
  { M           = Word V₄.Gen
  ; _·_         = _++_
  ; ε           = []
  ; ·-assoc     = λ a b c → V₄.++-assoc a b c
  ; ·-identityˡ = ++-identity-left
  ; ·-identityʳ = ++-identity-right
  ; degree      = λ w → parity (length w)
  ; degree-ε    = refl
  ; degree-·    = λ a b →
      trans (cong parity (length-distrib a b))
            (parity-+ (length a) (length b))
  }

------------------------------------------------------------------------
-- N-2: Capstone.
--
-- After this slice, V₄-Coxeter is the substrate's first concrete
-- F₂-graded monoid instance. The grading is by word-length parity;
-- combined with parity-+, the grading respects the monoid composition.
--
-- The pattern generalizes to ALL Coxeter instances: any (Word A, ++,
-- ε) gets an F₂-grading via length ∘ parity, with the homomorphism
-- property following from length-distrib + parity-+.
------------------------------------------------------------------------
