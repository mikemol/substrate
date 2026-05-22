------------------------------------------------------------------------
-- Substrate.Groups.Coxeter.Core.HigherArity.Step
--
-- The single arity-step combinator: cons a Word onto a normalize-
-- equation, lifting it through one level of the right-associated
-- ++ chain.
--
--   normalize-cons a (ih : normalize rest ≡ normalize rest')
--     : normalize (a ++ rest) ≡ normalize (normalize a ++ rest')
--
-- Every leaf in HigherArity.{Triple, Quad, Quint, Sext, Sept} is
-- exactly `normalize-cons a (previous-arity-lemma ...)`. Extracting
-- this combinator deduplicates the
--   `trans (normalize-append a _) (normalize-cong-right (normalize a) _)`
-- body shared across all five.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

open import Substrate.Foundation.Eq using (_≡_; trans)

module Substrate.Groups.Coxeter.Core.HigherArity.Step
  (Word : Set)
  (_++_ : Word → Word → Word)
  (Canonical : Word → Set)
  (normalize : Word → Word)
  (normalize-canonical : (w : Word) → Canonical (normalize w))
  (canonical-is-fixed : {w : Word} → Canonical w → normalize w ≡ w)
  (normalize-distrib :
    (a b : Word) → normalize (a ++ b) ≡ normalize (normalize a ++ normalize b))
  where

open import Substrate.Groups.Coxeter.Core.NormalizeAppend
  Word _++_ Canonical normalize normalize-canonical canonical-is-fixed normalize-distrib
open import Substrate.Groups.Coxeter.Core.NormalizeCong
  Word _++_ Canonical normalize normalize-canonical canonical-is-fixed normalize-distrib

normalize-cons : (a : Word) {rest rest' : Word} →
                 normalize rest ≡ normalize rest' →
                 normalize (a ++ rest) ≡ normalize (normalize a ++ rest')
normalize-cons a {rest} ih =
  trans (normalize-append a rest)
        (normalize-cong-right (normalize a) ih)
