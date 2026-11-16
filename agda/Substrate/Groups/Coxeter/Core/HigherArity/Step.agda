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


-- ⚑ A NAME USED IN THE TELESCOPE MUST BE IMPORTED BEFORE THE MODULE HEADER.
-- A parameter list is scope-checked before anything inside `where`, so an
-- import placed after the header is too late.  The splitter emits the
-- prelude after the header (right for a body, wrong for a telescope), so
-- every leaf whose PARAMETERS mention the name inherited this.
-- MEASURED: 11 sites tree-wide.
open import Substrate.Foundation.Eq
open import Substrate.Foundation.List
open import Substrate.Algebra.Quotient.Canonical
-- ⚑⚑ `…NormalizeAppend.Left` WAS IMPORTED HERE AND IS NOT — the THIRD and last instance of
-- the two-path ambiguity, after `NormalizeCong/Right.agda` and `NormalizeCong/Left.agda`.
-- Same shape: this UNAPPLIED leaf import plus `:44`'s import of the PARENT applied to its
-- telescope, which re-exports the leaf `public`. One definition, two paths, Agda cannot choose.
-- ⚑ THE POPULATION WAS PREDICTED, NOT DISCOVERED BY ITERATION. `--importers
-- Substrate.Groups.Coxeter.Core.NormalizeAppend` shows exactly TWO modules importing both the
-- parent and a leaf — this one and `NormalizeCong.Left` — and the compiler then confirmed both.
-- `--collide normalize-append` reports ONE provider and sees nothing, because the ambiguity is
-- two IMPORT PATHS to one definition rather than two definitions.
-- ⚑⚑⚑ AND `NormalizeCong.Right` WAS THE SAME DEFECT ONE FAMILY UP — I KEPT IT ON A WRONG
-- ARGUMENT. The comment here read: *"NormalizeCong.Right is a DIFFERENT module, not a second
-- path to the same name; it stays."* True that it is a different module, and IRRELEVANT: `:56`
-- imports the `NormalizeCong` PARENT applied, and that parent re-exports `.Right` `public`, so
-- an unapplied `.Right` import was a second path to `normalize-cong-right` exactly as the
-- `NormalizeAppend` pair was. The compiler said so on the next run.
-- ⚑ THE MISS WAS A SCOPED CENSUS READ AS A COMPLETE ONE: I ran `--importers` on
-- `…NormalizeAppend` and treated its two-module answer as the whole population, when the same
-- query on `…NormalizeCong` names THIS FILE as its one external offender. Two families, one
-- shape; asking about one is not asking about both.

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
open import Substrate.Foundation.Eq
open import Substrate.Foundation.Eq.Trans

normalize-cons : (a : Word) {rest rest' : Word} →
                 normalize rest ≡ normalize rest' →
                 normalize (a ++ rest) ≡ normalize (normalize a ++ rest')
normalize-cons a {rest} ih =
  trans (normalize-append a rest)
        (normalize-cong-right (normalize a) ih)
