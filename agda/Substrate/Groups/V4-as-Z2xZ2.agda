------------------------------------------------------------------------
-- Substrate.Groups.V4-as-Z2xZ2
--
-- V₄ ≅ Z/2 × Z/2, as the Coxeter direct product of TWO COPIES of the
-- SAME group (Z/2 = Cyclic index 1). Both factors are index 1; the
-- duplication is the point, not two carriers.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Groups.V4-as-Z2xZ2 where

open import Substrate.Groups.Coxeter.Word using (Word; _++_; ++-assoc)
open import Substrate.Groups.Coxeter.Cyclic.Base 1 using (Gen)
open import Substrate.Groups.Coxeter.Cyclic.Core 1
  using (ε; canonical-is-fixed; normalize-distrib)
open import Substrate.Groups.Coxeter.Cyclic.Existential 1
  using (Canonical-ex; normalize; normalize-canonical)

open import Substrate.Groups.Coxeter.DirectProduct
  (Word Gen) _++_ ε ++-assoc
    Canonical-ex normalize normalize-canonical
    canonical-is-fixed normalize-distrib
  (Word Gen) _++_ ε ++-assoc
    Canonical-ex normalize normalize-canonical
    canonical-is-fixed normalize-distrib
  public
