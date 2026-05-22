------------------------------------------------------------------------
-- Substrate.Groups.Coxeter.Core
--
-- Abstract Coxeter Core. Parameterized over a Word type with a
-- monoid structure (++/ε with associativity + identity laws) and a
-- normalization function with canonical-form predicate. The shape
-- of Word is opaque — this Core works equally well for `List Gen`
-- (Coxeter group presentations via generator words) and for
-- `Word₁ × Word₂` (direct products of Coxeter groups), among other
-- encodings.
--
-- Per [[feedback-v4-typeclass-architecture]]: any normalization-
-- bearing monoid satisfying the below interface inherits the entire
-- foundation (group ops, bridge lemmas, clash macro, composition
-- helpers).
--
-- Section-per-file (each section is itself a parametric submodule
-- sharing the same Word/normalize/etc. interface):
--
--   Core.Operations          — _·_ / _≈_ / _≉_ / ε
--   Core.NormalizeIdem       — idempotency of normalize
--   Core.NormalizeAppend     — left/right asymmetric distributors
--   Core.NormalizeCongRight  — cong-right at normalize level
--   Core.HigherArity         — triple / quad / quint / sext / sept
--   Core.IdemInequality      — ≉-idem lifting
--   Core.Clash               — Canonical-vs-≉ ⊥-elim macro
--   Core.AssocFour           — 4-way associativity
--
-- INSTANTIATIONS (existing or planned):
--   * Substrate.Groups.Coxeter.ListPresentation : List Gen + insert
--   * Substrate.Groups.Coxeter.DirectProduct    : Word₁ × Word₂
--
-- ADAPTER WRAPPERS use this Core; THEOREMS (finite enumerations like
-- V₄-4-product) live with the specific instance.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

open import Substrate.Foundation.Eq using (_≡_)

module Substrate.Groups.Coxeter.Core
  (Word : Set)
  (_++_ : Word → Word → Word)
  (ε-in : Word)
  (++-assoc : (a b c : Word) → (a ++ b) ++ c ≡ a ++ (b ++ c))
  (Canonical : Word → Set)
  (normalize : Word → Word)
  (normalize-canonical : (w : Word) → Canonical (normalize w))
  (canonical-is-fixed : {w : Word} → Canonical w → normalize w ≡ w)
  (normalize-distrib :
    (a b : Word) → normalize (a ++ b) ≡ normalize (normalize a ++ normalize b))
  where

open import Substrate.Groups.Coxeter.Core.Operations
  Word _++_ ε-in normalize public

open import Substrate.Groups.Coxeter.Core.NormalizeIdem
  Word Canonical normalize normalize-canonical canonical-is-fixed public

open import Substrate.Groups.Coxeter.Core.NormalizeAppend
  Word _++_ Canonical normalize normalize-canonical canonical-is-fixed normalize-distrib public

open import Substrate.Groups.Coxeter.Core.NormalizeCongRight
  Word _++_ Canonical normalize normalize-canonical canonical-is-fixed normalize-distrib public

open import Substrate.Groups.Coxeter.Core.HigherArity
  Word _++_ Canonical normalize normalize-canonical canonical-is-fixed normalize-distrib public

open import Substrate.Groups.Coxeter.Core.IdemInequality
  Word Canonical normalize normalize-canonical canonical-is-fixed public

open import Substrate.Groups.Coxeter.Core.Clash
  Word Canonical normalize public

open import Substrate.Groups.Coxeter.Core.AssocFour
  Word _++_ ++-assoc public
