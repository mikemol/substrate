------------------------------------------------------------------------
-- Substrate.Groups.Coxeter.Core.IdemInequality
--
-- Section 6 of Coxeter.Core. Inequality lifting through normalize.
-- Used by per-instance finite-enumeration theorems to bridge `≉`
-- hypotheses across the implicit-Word substitution that happens when
-- applying eval-canonical to `normalize-canonical w`.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

open import Substrate.Foundation.Eq using (_≡_; _≢_; trans; sym)

module Substrate.Groups.Coxeter.Core.IdemInequality
  (Word : Set)
  (Canonical : Word → Set)
  (normalize : Word → Word)
  (normalize-canonical : (w : Word) → Canonical (normalize w))
  (canonical-is-fixed : {w : Word} → Canonical w → normalize w ≡ w)
  where

open import Substrate.Groups.Coxeter.Core.NormalizeIdem
  Word Canonical normalize normalize-canonical canonical-is-fixed

private
  _≉_ : Word → Word → Set
  w₁ ≉ w₂ = normalize w₁ ≢ normalize w₂

≉-idem : (w₁ w₂ : Word) → w₁ ≉ w₂ → normalize w₁ ≉ normalize w₂
≉-idem w₁ w₂ neq p =
  neq (trans (sym (normalize-idem w₁)) (trans p (normalize-idem w₂)))
