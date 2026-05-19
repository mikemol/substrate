------------------------------------------------------------------------
-- Substrate.Groups.V4-Coxeter-F2Graded-CountA
--
-- A SECOND F₂-grading on V₄-Coxeter: count of A generators, mod 2.
--
-- Where length-parity (slice 15) splits V₄ as {ε, AB} (degree 0) vs
-- {A, B} (degree 1), the count-A-parity splits V₄ as {ε, B} (degree 0)
-- vs {A, AB} (degree 1).
--
-- These are two DIFFERENT F₂-gradings on V₄, both monoid
-- homomorphisms. Together with count-B-parity (a third grading), the
-- three F₂-gradings give the V₄ ≅ Z/2 × Z/2 coordinate isomorphism:
--
--   V₄ element  | length-parity | count-A-parity | count-B-parity
--   ε           | 𝟘             | 𝟘              | 𝟘
--   A           | 𝟙             | 𝟙              | 𝟘
--   B           | 𝟙             | 𝟘              | 𝟙
--   AB          | 𝟘             | 𝟙              | 𝟙
--
-- The (count-A-parity, count-B-parity) pair coordinate IS the Z/2 ×
-- Z/2 isomorphism explicitly.
--
-- Note on the 3+1 parity universal: the substrate's 3+1 split
-- (V₄-Nonzero = {A, B, AB} vs identity ε) is a CARRIER-SET
-- DECOMPOSITION, not an F₂-grading. V₄-Nonzero isn't closed under ·
-- (e.g., A · A = ε ∈ identity, not in Nonzero). The 3+1 is structural
-- partition + a separate identity-indicator, not a single monoid
-- homomorphism to F₂.
--
-- Per [[project-3plus1-as-graded-cocycle]] (with this correction):
-- the 3+1 grading framing was OVERSPECIFIED — V₄ has THREE
-- independent F₂-gradings (length-parity, count-A-parity,
-- count-B-parity), none of which directly correspond to the 3+1
-- carrier-set split. The graded readings are non-trivially related.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Groups.V4-Coxeter-F2Graded-CountA where

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
-- N-1: count-A — count of A generators in a V₄ word.
------------------------------------------------------------------------

count-A : Word V₄.Gen → ℕ
count-A []          = zero
count-A (V₄.A ∷ w)  = suc (count-A w)
count-A (V₄.B ∷ w)  = count-A w

------------------------------------------------------------------------
-- N-2: count-A is additive (monoid homomorphism into ℕ).
------------------------------------------------------------------------

count-A-distrib :
  (a b : Word V₄.Gen) →
  count-A (a ++ b) ≡ count-A a + count-A b
count-A-distrib []          b = refl
count-A-distrib (V₄.A ∷ a)  b = cong suc (count-A-distrib a b)
count-A-distrib (V₄.B ∷ a)  b = count-A-distrib a b

------------------------------------------------------------------------
-- N-3: V₄ as F₂-graded by count-A-parity.
------------------------------------------------------------------------

V4-F2Graded-CountA : RGradedMonoid F₂-CommMonoid _
V4-F2Graded-CountA = record
  { M           = Word V₄.Gen
  ; _·_         = _++_
  ; ε           = []
  ; ·-assoc     = λ a b c → V₄.++-assoc a b c
  ; ·-identityˡ = ++-identity-left
  ; ·-identityʳ = ++-identity-right
  ; degree      = λ w → parity (count-A w)
  ; degree-ε    = refl
  ; degree-·    = λ a b →
      trans (cong parity (count-A-distrib a b))
            (parity-+ (count-A a) (count-A b))
  }

------------------------------------------------------------------------
-- N-4: Capstone.
--
-- After this slice, V₄ has TWO F₂-gradings (length-parity and
-- count-A-parity). The pattern generalizes: count-B-parity would
-- be a third grading; the (count-A, count-B) pair gives the V₄ ≅
-- Z/2 × Z/2 coordinate iso.
--
-- The 3+1 parity universal turns out to be CARRIER-SET structure,
-- not monoid grading. Slice 17 explores the V₄-Nonzero subset (the
-- "3" of the 3+1) explicitly.
------------------------------------------------------------------------
