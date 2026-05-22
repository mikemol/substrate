------------------------------------------------------------------------
-- Substrate.Category.ComposedReference.BasisLabel
--
-- Basis labels for the binding axis (mirrors Substrate.BasisState).
-- ALGEBRAIC / SPECTRAL + the four isotypic variants address the
-- chirality between substrate-aligned and structure-agnostic
-- interpretations of the emission payload.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Category.ComposedReference.BasisLabel where

data BasisLabel : Set where
  ALGEBRAIC        : BasisLabel
  SPECTRAL         : BasisLabel
  ISOTYPIC-TRIV    : BasisLabel
  ISOTYPIC-SIGN    : BasisLabel
  ISOTYPIC-STD     : BasisLabel
  ISOTYPIC-STDSGN  : BasisLabel
  ISOTYPIC-2D      : BasisLabel
