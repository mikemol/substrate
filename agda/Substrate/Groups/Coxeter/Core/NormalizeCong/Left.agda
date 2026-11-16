------------------------------------------------------------------------
-- Substrate.Groups.Coxeter.Core.NormalizeCong.Left
--
-- normalize-cong-left b eq :
--   normalize (a₁ ++ b) ≡ normalize (a₂ ++ b)
-- given eq : normalize a₁ ≡ normalize a₂.
--
-- Mirror of NormalizeCong.Right — pulled out as a sibling so the
-- chirality pair is exposed at the file boundary. Closes via the
-- left asymmetric distributor: peel normalize off the left operand
-- on both sides, apply cong, peel back.
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
-- ⚑⚑ `…NormalizeAppend.Left` WAS IMPORTED HERE AND IS NOT — the MIRROR of the same defect in
-- the sibling `NormalizeCong/Right.agda`, identical down to the line numbers (:26 unapplied,
-- :39 applied). One splitter emitted both. It produced [AmbiguousName] on `normalize-append`:
-- ONE definition (NormalizeAppend/Left.agda:43) reached this module by TWO paths — this
-- UNAPPLIED leaf import, and :39's import of the PARENT applied to all seven telescope
-- parameters, which re-exports the leaf `public`.
-- ⚑ NO CENSUS REPORTS THIS: `--collide normalize-append` finds ONE provider, because the
-- ambiguity is two IMPORT PATHS to one definition, not two definitions. What DOES find it is
-- `--importers` on the parent — exactly two modules import both the parent and a leaf
-- (this one and `HigherArity.Step`), and that pair IS the population.

module Substrate.Groups.Coxeter.Core.NormalizeCong.Left
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
open import Substrate.Foundation.Eq
open import Substrate.Foundation.Eq.Trans
open import Substrate.Foundation.Eq.Sym
open import Substrate.Foundation.Eq.Cong
open import Substrate.Foundation.Eq.TransSym

normalize-cong-left : (b : Word) {a₁ a₂ : Word} →
                      normalize a₁ ≡ normalize a₂ →
                      normalize (a₁ ++ b) ≡ normalize (a₂ ++ b)
normalize-cong-left b {a₁} {a₂} eq =
  trans (normalize-append a₁ b)
  (trans-sym (cong (λ x → normalize (x ++ b)) eq)
             (normalize-append a₂ b))
