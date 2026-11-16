------------------------------------------------------------------------
-- Substrate.Groups.Coxeter.Core.NormalizeCong.Right
--
-- normalize-cong-right a eq :
--   normalize (a ++ b₁) ≡ normalize (a ++ b₂)
-- given eq : normalize b₁ ≡ normalize b₂.
--
-- Closes via the right asymmetric distributor: peel normalize off the
-- right operand on both sides, apply cong, peel back. Mirror of
-- NormalizeCong.Left — exposed as a sibling pair so the similarity
-- checker can surface the chirality structure.
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
-- ⚑⚑ `…NormalizeAppend.Right` WAS IMPORTED HERE AND IS NOT. It produced [AmbiguousName] on
-- `normalize-append-right`: ONE definition (NormalizeAppend/Right.agda:44) reached this module
-- by TWO paths — this UNAPPLIED leaf import, and `:39`'s import of the PARENT applied to all
-- seven telescope parameters, which re-exports the leaf `public` (NormalizeAppend:41) with those
-- same seven. Agda cannot choose between them.
-- ⚑ THE APPLIED PATH IS THE CORRECT ONE and this was also the WRONG one: it bound the leaf
-- unapplied. The hoist rationale above covers names used in the TELESCOPE (:29-36) — which
-- never mentions `normalize-append-right` — so this line was never justified by it.

module Substrate.Groups.Coxeter.Core.NormalizeCong.Right
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

normalize-cong-right : (a : Word) {b₁ b₂ : Word} →
                       normalize b₁ ≡ normalize b₂ →
                       normalize (a ++ b₁) ≡ normalize (a ++ b₂)
normalize-cong-right a {b₁} {b₂} eq =
  trans (normalize-append-right a b₁)
  (trans-sym (cong (λ x → normalize (a ++ x)) eq)
             (normalize-append-right a b₂))
