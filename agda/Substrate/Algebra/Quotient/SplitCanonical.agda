------------------------------------------------------------------------
-- Substrate.Algebra.Quotient.SplitCanonical
--
-- Defines: split-Canonical
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.Algebra.Quotient; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.Quotient.SplitCanonical where

open import Agda.Primitive
open import Substrate.Algebra.Quotient.Canonical
open import Substrate.Algebra.Quotient.KerQuotient
open import Substrate.Foundation.Eq
open import Substrate.Foundation.Eq.Cong
open import Substrate.Foundation.Eq.Sym



-- A retraction F∘s≡id splits the idempotent e = s∘F, which IS a Canonical
-- form for ker F. All four laws fall out of `retract` + `cong s`.
split-Canonical :
  {a b : Level} {A : Set a} {B : Set b}
  (F : A → B) (s : B → A) (retract : (y : B) → F (s y) ≡ y) →
  Canonical (ker-Quotient F)
split-Canonical F s retract = record
  { canonical            = λ a → s (F a)
  ; canonical-idempotent = λ a → cong s (retract (F a))
  ; canonical-respects-≈ = λ e → cong s e
  ; ≈-canonical          = λ a → sym (retract (F a))
  }
