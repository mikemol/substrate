------------------------------------------------------------------------
-- Substrate.Groups.Z4-x-FreeCyclic
--
-- The 2-D word algebra Z₄ × ℕ — thin instantiation of the parametric
-- Zn-x-FreeCyclic module.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Groups.Z4-x-FreeCyclic where

import Substrate.Groups.Z4-Coxeter as Z₄

open import Substrate.Groups.Zn-x-FreeCyclic
  (Z₄.Word Z₄.Gen) (Z₄._++_) Z₄.ε Z₄.++-assoc
    Z₄.Canonical Z₄.normalize Z₄.normalize-canonical
    Z₄.canonical-is-fixed-Z4 Z₄.normalize-distrib
  public
