------------------------------------------------------------------------
-- Substrate.Groups.Coxeter.Core.IdemInequality
--
-- Section 6 of Coxeter.Core. Inequality lifting through normalize.
-- Used by per-instance finite-enumeration theorems to bridge `≉`
-- hypotheses across the implicit-Word substitution that happens when
-- applying eval-canonical to `normalize-canonical w`.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}


-- ⚑ `_≡_` is used in the TELESCOPE below, so its import must PRECEDE the
-- module header: a parameter list is scope-checked before anything inside
-- `where`.  The splitter emits the prelude AFTER the header (correct for a
-- body, wrong for a telescope), so every leaf whose parameters mention `≡`
-- inherited this.  MEASURED: 6 of the Core leaves.
open import Substrate.Foundation.Eq
open import Substrate.Algebra.Quotient.Canonical

module Substrate.Groups.Coxeter.Core.IdemInequality
  (Word : Set)
  (Canonical : Word → Set)
  (normalize : Word → Word)
  (normalize-canonical : (w : Word) → Canonical (normalize w))
  (canonical-is-fixed : {w : Word} → Canonical w → normalize w ≡ w)
  where

-- ⚑ `Op` IS OPENED **WITHOUT** `public`, AND THAT IS THE PRE-SPLIT SEMANTICS.
-- Before R9 split it, `_≉_` was a `private` helper in this module (recovered
-- source at `pre-r9`, lines 35-37) — deliberately unexported, because
-- `Core/Operations.agda:44` already defines the SAME operator, byte-identical.
-- R9 turned the private block into a leaf and the root re-exported it, so
-- `Core.agda` saw two `_≉_` and failed [ClashingDefinition].
--
-- Re-exporting is what breaks; the leaf itself is correct.  `Idem` imports `Op`
-- directly (it needs `_≉_` in its own type), and nothing outside this subtree
-- ever wanted this definition — `Operations` is the public one.
open import Substrate.Groups.Coxeter.Core.IdemInequality.Op Word Canonical normalize normalize-canonical canonical-is-fixed
-- ⚑ `public` RETIRED (Ⓑ2c).  Note the comment above already records that
-- *"re-exporting is what breaks"* — for `Op`, whose forward caused a
-- ClashingDefinition in `Core.agda`.  The same construct on `Idem` was left
-- standing; this retires it, so `Core` applies the leaf itself.
open import Substrate.Groups.Coxeter.Core.IdemInequality.Idem Word Canonical normalize normalize-canonical canonical-is-fixed
