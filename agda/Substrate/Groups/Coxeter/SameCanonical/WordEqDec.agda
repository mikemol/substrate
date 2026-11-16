------------------------------------------------------------------------
-- Substrate.Groups.Coxeter.SameCanonical.WordEqDec
--
-- Defines: Word-≡-Dec
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.Groups.Coxeter.SameCanonical; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Groups.Coxeter.SameCanonical.WordEqDec where

open import Substrate.Foundation.Negation.Dec
open import Substrate.Groups.Coxeter.Word
open import Substrate.Foundation.Eq
open import Substrate.Foundation.Eq.Cong
open import Substrate.Groups.Coxeter.SameCanonical.Private
open import Substrate.Groups.Coxeter.SameCanonical.ConsHead
open import Substrate.Groups.Coxeter.SameCanonical.ConsTail



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
