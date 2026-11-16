------------------------------------------------------------------------
-- Substrate.Groups.Coxeter.Core.NormalizeAppend.Left
--
-- normalize-append:
--   normalize (a ++ b) ≡ normalize (normalize a ++ b)
-- The "left" asymmetric distributor — pulls normalize through to the
-- left operand. Derived from normalize-distrib + normalize-idem.
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

module Substrate.Groups.Coxeter.Core.NormalizeAppend.Left
  (Word : Set)
  (_++_ : Word → Word → Word)
  (Canonical : Word → Set)
  (normalize : Word → Word)
  (normalize-canonical : (w : Word) → Canonical (normalize w))
  (canonical-is-fixed : {w : Word} → Canonical w → normalize w ≡ w)
  (normalize-distrib :
    (a b : Word) → normalize (a ++ b) ≡ normalize (normalize a ++ normalize b))
  where

open import Substrate.Groups.Coxeter.Core.NormalizeIdem
  Word Canonical normalize normalize-canonical canonical-is-fixed
open import Substrate.Foundation.Eq
open import Substrate.Foundation.Eq.Trans
open import Substrate.Foundation.Eq.Sym
open import Substrate.Foundation.Eq.Cong
open import Substrate.Foundation.Eq.TransSym


normalize-append : (a b : Word) → normalize (a ++ b) ≡ normalize (normalize a ++ b)
normalize-append a b =
  trans-sym (normalize-distrib a b)
            (trans (normalize-distrib (normalize a) b)
                   (cong (λ x → normalize (x ++ normalize b))
                         (normalize-idem a)))
