------------------------------------------------------------------------
-- Substrate.Groups.Coxeter.Core.HigherArity
--
-- Section 5 of Coxeter.Core. Higher-arity distribution ladder,
-- decomposed file-per-lemma to expose the inductive shape to the
-- similarity checker:
--
--   HigherArity.Step    — normalize-cons (the shared arity-step combinator)
--   HigherArity.Triple  — 3 operands  (V₄ etc.)
--   HigherArity.Quad    — 4 operands  (V₄-4-product)
--   HigherArity.Quint   — 5 operands  (Z₅ fifth-power)
--   HigherArity.Sext    — 6 operands  (Zₙ sixth-power)
--   HigherArity.Sept    — 7 operands  (Z₇ seventh-power)
--
-- Each leaf is `normalize-cons a (previous-arity-lemma ...)` — the
-- single `normalize-append + normalize-cong-right` step is extracted
-- in `HigherArity.Step` as `normalize-cons`, and every Triple…Sept
-- leaf is a one-line specialization. Consumer surfaces (the
-- per-arity names) are preserved.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

open import Substrate.Foundation.Eq using (_≡_)

module Substrate.Groups.Coxeter.Core.HigherArity
  (Word : Set)
  (_++_ : Word → Word → Word)
  (Canonical : Word → Set)
  (normalize : Word → Word)
  (normalize-canonical : (w : Word) → Canonical (normalize w))
  (canonical-is-fixed : {w : Word} → Canonical w → normalize w ≡ w)
  (normalize-distrib :
    (a b : Word) → normalize (a ++ b) ≡ normalize (normalize a ++ normalize b))
  where

open import Substrate.Groups.Coxeter.Core.HigherArity.Step
  Word _++_ Canonical normalize normalize-canonical canonical-is-fixed normalize-distrib public

open import Substrate.Groups.Coxeter.Core.HigherArity.Triple
  Word _++_ Canonical normalize normalize-canonical canonical-is-fixed normalize-distrib public

open import Substrate.Groups.Coxeter.Core.HigherArity.Quad
  Word _++_ Canonical normalize normalize-canonical canonical-is-fixed normalize-distrib public

open import Substrate.Groups.Coxeter.Core.HigherArity.Quint
  Word _++_ Canonical normalize normalize-canonical canonical-is-fixed normalize-distrib public

open import Substrate.Groups.Coxeter.Core.HigherArity.Sext
  Word _++_ Canonical normalize normalize-canonical canonical-is-fixed normalize-distrib public

open import Substrate.Groups.Coxeter.Core.HigherArity.Sept
  Word _++_ Canonical normalize normalize-canonical canonical-is-fixed normalize-distrib public
