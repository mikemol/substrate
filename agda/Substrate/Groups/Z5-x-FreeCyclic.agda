------------------------------------------------------------------------
-- Substrate.Groups.Z5-x-FreeCyclic
--
-- The 2-D word algebra Z₅ × ℕ — thin instantiation of the parametric
-- Zn-x-FreeCyclic module.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Groups.Z5-x-FreeCyclic where

import Substrate.Groups.Z5-Coxeter as Z₅

open import Substrate.Groups.Zn-x-FreeCyclic
  (Z₅.Word Z₅.Gen) (Z₅._++_) Z₅.ε Z₅.++-assoc
    Z₅.Canonical Z₅.normalize Z₅.normalize-canonical
    Z₅.canonical-is-fixed Z₅.normalize-distrib
  public
