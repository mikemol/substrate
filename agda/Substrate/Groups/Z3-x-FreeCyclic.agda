------------------------------------------------------------------------
-- Substrate.Groups.Z3-x-FreeCyclic
--
-- The 2-D word algebra Z₃ × ℕ — thin instantiation of the parametric
-- Zn-x-FreeCyclic module.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Groups.Z3-x-FreeCyclic where

import Substrate.Groups.Z3-Coxeter as Z₃

open import Substrate.Groups.Zn-x-FreeCyclic
  (Z₃.Word Z₃.Gen) (Z₃._++_) Z₃.ε Z₃.++-assoc
    Z₃.Canonical Z₃.normalize Z₃.normalize-canonical
    Z₃.canonical-is-fixed-Z3 Z₃.normalize-distrib
  public
