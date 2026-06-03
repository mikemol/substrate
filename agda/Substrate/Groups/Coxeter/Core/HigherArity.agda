------------------------------------------------------------------------
-- Substrate.Groups.Coxeter.Core.HigherArity
--
-- Section 5 of Coxeter.Core. Higher-arity distribution.
--
--   HigherArity.Step    — normalize-cons (the shared arity-step combinator)
--   HigherArity.Chain   — normalize-chain : the GENERIC arity lemma over
--                         Vec Word (suc n); any arity is free, no new file.
--   HigherArity.Triple  — normalize-triple (named arity-3 instance of Chain)
--   HigherArity.Quad    — normalize-quad   (named arity-4 instance; the one
--                         live consumer is V4-Coxeter)
--
-- The former file-per-arity ladder (Quint/Sext/Sept) was an open-ended
-- antipattern — every new arity meant a new file — and Quint/Sext/Sept had
-- ZERO consumers. Replaced by the single inductive normalize-chain; the two
-- live named rungs (Triple, Quad) now derive from it in one line.
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

open import Substrate.Groups.Coxeter.Core.HigherArity.Chain
  Word _++_ Canonical normalize normalize-canonical canonical-is-fixed normalize-distrib public

open import Substrate.Groups.Coxeter.Core.HigherArity.Triple
  Word _++_ Canonical normalize normalize-canonical canonical-is-fixed normalize-distrib public

open import Substrate.Groups.Coxeter.Core.HigherArity.Quad
  Word _++_ Canonical normalize normalize-canonical canonical-is-fixed normalize-distrib public
