------------------------------------------------------------------------
-- Substrate.Groups.Coxeter.SameCanonical
--
-- Generic `same-canonical` lifter for Coxeter groups.
--
-- INSIGHT (per [[feedback-expose-generator-not-orbit]] applied to
-- Zₙ-Coxeter's same-canonical enumerations): the `Canonical w₁`,
-- `Canonical w₂` parameters are UNUSED in deciding `w₁ ≡ w₂`. The
-- decision is decidable equality on the underlying Word — which
-- holds whenever Gen has decidable equality.
--
-- One Word-level lifter, parametric in `_≟Gen_ : DecidableEquality
-- Gen`, replaces ~187 refl lines across 5 files (Z2/Z3/Z4/Z5/Z7/
-- V4-Coxeter).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Groups.Coxeter.SameCanonical where

open import Substrate.Foundation.Eq using (_≡_; refl; cong)
open import Substrate.Foundation.Negation using (Dec; yes; no)

open import Substrate.Groups.Coxeter.Word using (Word; []; _∷_)

------------------------------------------------------------------------
-- Word-level decidable equality, parametric in Gen.
--
-- This IS the single generic fact: from decidable Gen, derive
-- decidable Word Gen. Each Zₙ-Coxeter same-canonical reduces to
-- calling this with the group's Gen-decidable-equality.
------------------------------------------------------------------------

private
  -- ∷-injection: head + tail equality from cons equality.
  ∷-head : {Gen : Set} {x y : Gen} {xs ys : Word Gen} →
           (x ∷ xs) ≡ (y ∷ ys) → x ≡ y
  ∷-head refl = refl

  ∷-tail : {Gen : Set} {x y : Gen} {xs ys : Word Gen} →
           (x ∷ xs) ≡ (y ∷ ys) → xs ≡ ys
  ∷-tail refl = refl

Word-≡-Dec :
  {Gen : Set} →
  ((g₁ g₂ : Gen) → Dec (g₁ ≡ g₂)) →
  (w₁ w₂ : Word Gen) → Dec (w₁ ≡ w₂)
Word-≡-Dec _≟Gen_ []       []       = yes refl
Word-≡-Dec _≟Gen_ []       (_ ∷ _)  = no (λ ())
Word-≡-Dec _≟Gen_ (_ ∷ _)  []       = no (λ ())
Word-≡-Dec _≟Gen_ (g₁ ∷ ws₁) (g₂ ∷ ws₂)
  with g₁ ≟Gen g₂ | Word-≡-Dec _≟Gen_ ws₁ ws₂
... | yes refl | yes refl = yes refl
... | no  ¬eq  | _        = no (λ p → ¬eq (∷-head p))
... | _        | no  ¬eq  = no (λ p → ¬eq (∷-tail p))

------------------------------------------------------------------------
-- The `same-canonical` lifter.
--
-- Given decidable equality on Gen, produces `same-canonical` for any
-- Canonical predicate. The canonical witnesses are unused —
-- decidability of word equality is enough.
------------------------------------------------------------------------

same-canonical-via-Gen :
  {Gen : Set} {Canonical : Word Gen → Set} →
  ((g₁ g₂ : Gen) → Dec (g₁ ≡ g₂)) →
  {w₁ w₂ : Word Gen} → Canonical w₁ → Canonical w₂ → Dec (w₁ ≡ w₂)
same-canonical-via-Gen _≟Gen_ {w₁} {w₂} _ _ = Word-≡-Dec _≟Gen_ w₁ w₂
