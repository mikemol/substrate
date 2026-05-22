------------------------------------------------------------------------
-- Substrate.Groups.Z7-x-FreeCyclic
--
-- The 2-D word algebra Z₇ × ℕ — thin instantiation of the parametric
-- Zn-x-FreeCyclic module.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Groups.Z7-x-FreeCyclic where

import Substrate.Groups.Z7-Coxeter as Z₇

open import Substrate.Groups.Zn-x-FreeCyclic
  (Z₇.Word Z₇.Gen) (Z₇._++_) Z₇.ε Z₇.++-assoc
    Z₇.Canonical Z₇.normalize Z₇.normalize-canonical
    Z₇.canonical-is-fixed Z₇.normalize-distrib
  public
