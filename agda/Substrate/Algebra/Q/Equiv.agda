------------------------------------------------------------------------
-- Substrate.Algebra.Q.Equiv
--
-- Semantic equality on ℚ: cross-multiplication `a/b ≈ℚ c/d = a·d ≡ c·b`,
-- packaged as a `Quotient ℚ _≈ℚ_` — REUSING the wedge-adjacent
-- semantic-equality machinery `Substrate.Algebra.Quotient` (the same
-- `Quotient`/`Canonical` records `Algebra.Quotient.ModN` and the wedge
-- projection use). This is the equality the ℚ field laws hold over
-- (the unreduced-fraction `_≡_` makes the inverse laws syntactically false).
--
-- The Canonical extension (= `reduce`) stays deferred (Q.Reduction has the
-- `is-reduced` predicate but not the reduce function); the setoid alone carries
-- the field laws. Transitivity is the one nontrivial law — standard
-- cross-multiplication transitivity, cancelling the middle denominator
-- (`*ℤ-cancelʳ-pos`) after factor swaps (`*ℤ-swap₂₃`).
--
-- Zero postulates, --safe --without-K.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.Q.Equiv where

open import Substrate.Foundation.Nat using (suc)
open import Substrate.Foundation.Eq using (_≡_; refl; sym; trans; cong)
open import Substrate.Algebra.Z using (+_)
open import Substrate.Algebra.Z.Arithmetic using (_*ℤ_)
open import Substrate.Algebra.Z.Properties.MulFull using (*ℤ-cancelʳ-pos; *ℤ-swap₂₃)
open import Substrate.Algebra.Q using (ℚ; mkℚ; num; den-1)
open import Substrate.Algebra.Quotient using (Quotient)

------------------------------------------------------------------------
-- 1. Cross-multiplication equality. (den = suc (den-1), written literally so
--    the cancel-by-positive lemma's `+ suc d` form matches definitionally.)
------------------------------------------------------------------------

_≈ℚ_ : ℚ → ℚ → Set
p ≈ℚ q = (num p *ℤ (+ suc (den-1 q))) ≡ (num q *ℤ (+ suc (den-1 p)))

------------------------------------------------------------------------
-- 2. The setoid laws.
------------------------------------------------------------------------

≈ℚ-refl : (a : ℚ) → a ≈ℚ a
≈ℚ-refl a = refl

≈ℚ-sym : {a b : ℚ} → a ≈ℚ b → b ≈ℚ a
≈ℚ-sym e = sym e

≈ℚ-trans : {a b c : ℚ} → a ≈ℚ b → b ≈ℚ c → a ≈ℚ c
-- Projection form (no record-match on the implicits — that triggers an
-- eta coverage-stall). H1/H2 are ASCRIBED to their explicit `≡` types (a
-- definitional coercion, since `_≈ℚ_` unfolds to that `≡`) so `cong` can read
-- their endpoints.
≈ℚ-trans {a} {b} {c} H1 H2 = *ℤ-cancelʳ-pos _ _ (den-1 b) chain
  where
    h1 : (num a *ℤ (+ suc (den-1 b))) ≡ (num b *ℤ (+ suc (den-1 a)))
    h1 = H1
    h2 : (num b *ℤ (+ suc (den-1 c))) ≡ (num c *ℤ (+ suc (den-1 b)))
    h2 = H2
    chain : (num a *ℤ (+ suc (den-1 c))) *ℤ (+ suc (den-1 b))
          ≡ (num c *ℤ (+ suc (den-1 a))) *ℤ (+ suc (den-1 b))
    chain =
      trans (*ℤ-swap₂₃ (num a) (+ suc (den-1 c)) (+ suc (den-1 b)))
      (trans (cong (_*ℤ (+ suc (den-1 c))) h1)
      (trans (*ℤ-swap₂₃ (num b) (+ suc (den-1 a)) (+ suc (den-1 c)))
      (trans (cong (_*ℤ (+ suc (den-1 a))) h2)
             (*ℤ-swap₂₃ (num c) (+ suc (den-1 b)) (+ suc (den-1 a))))))

------------------------------------------------------------------------
-- 3. ℚ as a Quotient (reusing Algebra.Quotient).
------------------------------------------------------------------------

ℚ-Quotient : Quotient ℚ _≈ℚ_
ℚ-Quotient = record
  { ≈-refl  = ≈ℚ-refl
  ; ≈-sym   = λ {a} {b}     → ≈ℚ-sym   {a} {b}
  ; ≈-trans = λ {a} {b} {c} → ≈ℚ-trans {a} {b} {c}
  }
