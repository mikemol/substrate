------------------------------------------------------------------------
-- Substrate.Groups.Zn-Coxeter-Strict2Monoid
--
-- Parametric module: any Coxeter instance's Core data lifts to a
-- Strict2Monoid via FromCoxeter.
--
-- Consolidates the per-n Strict2Monoid wrappers (Z3, Z4, Z5) which
-- were each ~24-line files instantiating FromCoxeter with their
-- specific Coxeter data.
--
-- Each per-n file becomes a ~12-line thin instantiation of this
-- parametric module.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}


-- ⚑ A NAME USED IN THE TELESCOPE MUST BE IMPORTED BEFORE THE MODULE HEADER.
-- A parameter list is scope-checked before anything inside `where`, so an
-- import placed after the header is too late.  The splitter emits the
-- prelude after the header (right for a body, wrong for a telescope), so
-- every leaf whose PARAMETERS mention the name inherited this.
-- MEASURED: 11 sites tree-wide.
open import Substrate.Foundation.Eq
open import Substrate.Groups.Coxeter.Word
open import Substrate.Groups.Capabilities.Strict2Monoid

module Substrate.Groups.Zn-Coxeter-Strict2Monoid
  (Word          : Set)
  (_++_          : Word → Word → Word)
  (ε             : Word)
  (++-assoc      : (a b c : Word) → (a ++ b) ++ c ≡ a ++ (b ++ c))
  (++-identityˡ  : (a : Word) → ε ++ a ≡ a)
  (++-identityʳ  : (a : Word) → a ++ ε ≡ a)
  (normalize     : Word → Word)
  (normalize-distrib :
    (a b : Word) → normalize (a ++ b) ≡ normalize (normalize a ++ normalize b))
  where

open import Substrate.Category.Strict2Monoid.FromCoxeter
  Word _++_ ε ++-assoc
  ++-identityˡ ++-identityʳ
  normalize normalize-distrib
  public
open import Substrate.Foundation.Eq
