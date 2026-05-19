------------------------------------------------------------------------
-- Substrate.Groups.Z5-x-FreeCyclic
--
-- The 2-D word algebra Z₅ × ℕ via DirectProduct.
-- Mirror of Z3-x-FreeCyclic and Z4-x-FreeCyclic at n=5.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Groups.Z5-x-FreeCyclic where

import Substrate.Groups.Z5-Coxeter as Z₅
import Substrate.Groups.FreeCyclic-Coxeter as F

open import Substrate.Groups.Coxeter.DirectProduct
  (Z₅.Word Z₅.Gen) (Z₅._++_) Z₅.ε Z₅.++-assoc
    Z₅.Canonical Z₅.normalize Z₅.normalize-canonical
    Z₅.canonical-is-fixed-Z5 Z₅.normalize-distrib
  (F.Word F.Gen) (F._++_) F.ε F.++-assoc
    F.Canonical F.normalize F.normalize-canonical
    F.canonical-is-fixed-Free F.normalize-distrib
  public
