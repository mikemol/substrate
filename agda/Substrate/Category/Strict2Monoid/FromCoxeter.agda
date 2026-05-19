------------------------------------------------------------------------
-- Substrate.Category.Strict2Monoid.FromCoxeter
--
-- Constructor: any Coxeter Core instance gives a Strict2Monoid via
-- the (Word, _++_, ε, ≈) trio.
--
-- The mapping:
--   * M       = Word
--   * _·_     = _++_     (STRICT associative composition)
--   * ε       = ε        (empty word)
--   * _≈_     = normalize w₁ ≡ normalize w₂   (2-cell relation)
--   * ·-cong  = via normalize-distrib + cong (horizontal compose
--               of 2-cells respects ≈)
--
-- The 2-cell relation is propositional equality after normalization;
-- vertical composition is trans/sym on _≡_.
--
-- Note: this uses the WORD-LEVEL composition (strict), not the
-- normalize-then-compose `_·_` (which is weak/up-to-≈). The strict
-- version fits Strict2Monoid; the weak version would be a
-- Bicategory (deferred).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

open import Relation.Binary.PropositionalEquality
  using (_≡_; refl; sym; trans; cong)

module Substrate.Category.Strict2Monoid.FromCoxeter
  (Word : Set)
  (_++_ : Word → Word → Word)
  (ε : Word)
  (++-assoc : (a b c : Word) → (a ++ b) ++ c ≡ a ++ (b ++ c))
  (++-identity-left  : (a : Word) → ε ++ a ≡ a)
  (++-identity-right : (a : Word) → a ++ ε ≡ a)
  (normalize : Word → Word)
  (normalize-distrib :
    (a b : Word) → normalize (a ++ b) ≡ normalize (normalize a ++ normalize b))
  where

open import Substrate.Category.Strict2Monoid

------------------------------------------------------------------------
-- N-1: The 2-cell relation.
------------------------------------------------------------------------

_≈_ : Word → Word → Set
a ≈ b = normalize a ≡ normalize b

------------------------------------------------------------------------
-- N-2: Horizontal composition of 2-cells.
--
-- If a ≈ a' and b ≈ b' (i.e., normalize a ≡ normalize a' and
-- normalize b ≡ normalize b'), then a ++ b ≈ a' ++ b'.
--
-- Chain:
--   normalize (a ++ b)
--     ≡ normalize (normalize a ++ normalize b)          [normalize-distrib]
--     ≡ normalize (normalize a' ++ normalize b')        [cong₂ + premises]
--     ≡ normalize (a' ++ b')                            [sym normalize-distrib]
------------------------------------------------------------------------

·-cong : ∀ {a a' b b' : Word} → a ≈ a' → b ≈ b' → (a ++ b) ≈ (a' ++ b')
·-cong {a} {a'} {b} {b'} eq-a eq-b =
  trans (normalize-distrib a b)
  (trans (cong₂-≡ (λ x y → normalize (x ++ y)) eq-a eq-b)
         (sym (normalize-distrib a' b')))
  where
    -- Local cong₂ specialised to our binary signature.
    cong₂-≡ : ∀ {A B C : Set} (f : A → B → C) {a a' : A} {b b' : B} →
              a ≡ a' → b ≡ b' → f a b ≡ f a' b'
    cong₂-≡ f refl refl = refl

------------------------------------------------------------------------
-- N-3: The Strict2Monoid instance.
------------------------------------------------------------------------

Coxeter-Strict2Monoid : Strict2Monoid _ _
Coxeter-Strict2Monoid = record
  { M           = Word
  ; _·_         = _++_
  ; ε           = ε
  ; ·-assoc     = ++-assoc
  ; ·-identityˡ = ++-identity-left
  ; ·-identityʳ = ++-identity-right
  ; _≈_         = _≈_
  ; ≈-refl      = refl
  ; ≈-sym       = sym
  ; ≈-trans     = trans
  ; ·-cong      = ·-cong
  }

------------------------------------------------------------------------
-- N-4: Capstone.
--
-- After opening this module with a Coxeter instance's data, we get
-- the canonical Strict2Monoid for that Coxeter group. Used by:
--   * Z₃-Strict2Monoid (slice 3 omitted; can be added when needed)
--   * Z₄-Strict2Monoid
--   * V₄-Strict2Monoid (slice 3 — DirectProduct flavor)
--   * FreeCyclic-Strict2Monoid (slice 5 — graded flavor)
------------------------------------------------------------------------
