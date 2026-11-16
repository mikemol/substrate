------------------------------------------------------------------------
-- Substrate.Groups.Coxeter.Core.NormalizeAppend
--
-- Section 3 of Coxeter.Core. Asymmetric versions of normalize-distrib,
-- decomposed file-per-lemma:
--
--   NormalizeAppend.Left   — normalize (a ++ b) ≡ normalize (normalize a ++ b)
--   NormalizeAppend.Right  — normalize (a ++ b) ≡ normalize (a ++ normalize b)
--
-- Both close via normalize-distrib + normalize-idem. Each lemma
-- mirrors the other — exposed as separate files so the similarity
-- checker can surface the structural pair.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}


-- ⚑ `_≡_` is used in the TELESCOPE below, so its import must PRECEDE the
-- module header: a parameter list is scope-checked before anything inside
-- `where`.  The splitter emits the prelude AFTER the header (correct for a
-- body, wrong for a telescope), so every leaf whose parameters mention `≡`
-- inherited this.  MEASURED: 6 of the Core leaves.
open import Substrate.Foundation.Eq
open import Substrate.Foundation.List
open import Substrate.Algebra.Quotient.Canonical

module Substrate.Groups.Coxeter.Core.NormalizeAppend
  (Word : Set)
  (_++_ : Word → Word → Word)
  (Canonical : Word → Set)
  (normalize : Word → Word)
  (normalize-canonical : (w : Word) → Canonical (normalize w))
  (canonical-is-fixed : {w : Word} → Canonical w → normalize w ≡ w)
  (normalize-distrib :
    (a b : Word) → normalize (a ++ b) ≡ normalize (normalize a ++ normalize b))
  where

open import Substrate.Groups.Coxeter.Core.NormalizeAppend.Left
  Word _++_ Canonical normalize normalize-canonical canonical-is-fixed normalize-distrib public

open import Substrate.Groups.Coxeter.Core.NormalizeAppend.Right
  Word _++_ Canonical normalize normalize-canonical canonical-is-fixed normalize-distrib public
