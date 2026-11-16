------------------------------------------------------------------------
-- Substrate.Groups.Coxeter.Core.IdemInequality.Idem
--
-- Defines: ≉-idem
-- ⚑cap-128-forcing: one lemma, one elaboration unit (split horizontally
--   out of Substrate.Groups.Coxeter.Core.IdemInequality; telescope carried by split_telescoped).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

-- ⚑ these imports precede the module header BECAUSE THE TELESCOPE USES
--   them: a parameter list is scope-checked before anything in `where`.
open import Substrate.Foundation.Eq
open import Substrate.Algebra.Quotient.Canonical

module Substrate.Groups.Coxeter.Core.IdemInequality.Idem (Word : Set) (Canonical : Word → Set) (normalize : Word → Word) (normalize-canonical : (w : Word) → Canonical (normalize w)) (canonical-is-fixed : {w : Word} → Canonical w → normalize w ≡ w) where

open import Substrate.Groups.Coxeter.Core.NormalizeIdem
  Word Canonical normalize normalize-canonical canonical-is-fixed
open import Substrate.Groups.Coxeter.Core.IdemInequality.Op
  Word Canonical normalize normalize-canonical canonical-is-fixed
open import Substrate.Foundation.Eq.Neq
open import Substrate.Foundation.Eq.Trans
open import Substrate.Foundation.Eq.Sym


≉-idem : (w₁ w₂ : Word) → w₁ ≉ w₂ → normalize w₁ ≉ normalize w₂
≉-idem w₁ w₂ neq p =
  neq (trans (sym (normalize-idem w₁)) (trans p (normalize-idem w₂)))

