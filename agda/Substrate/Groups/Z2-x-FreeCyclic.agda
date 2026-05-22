------------------------------------------------------------------------
-- Substrate.Groups.Z2-x-FreeCyclic
--
-- The 2-D word algebra Z₂ × ℕ — thin instantiation of the parametric
-- Zn-x-FreeCyclic module.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Groups.Z2-x-FreeCyclic where

import Substrate.Groups.Z2-Coxeter as Z₂

open import Substrate.Groups.Zn-x-FreeCyclic
  (Z₂.Word Z₂.Gen) (Z₂._++_) Z₂.ε Z₂.++-assoc
    Z₂.Canonical Z₂.normalize Z₂.normalize-canonical
    Z₂.canonical-is-fixed-Z2 Z₂.normalize-distrib
  public
