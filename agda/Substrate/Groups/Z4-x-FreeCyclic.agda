------------------------------------------------------------------------
-- Substrate.Groups.Z4-x-FreeCyclic
--
-- The 2-D word algebra Z₄ × ℕ via DirectProduct of Z₄-Coxeter and
-- FreeCyclic-Coxeter.
--
-- Mirror of Z3-x-FreeCyclic at n=4. The phase axis (Z₄-Coxeter,
-- cyclic of order 4) paired with the cycle counter axis (FreeCyclic,
-- ℕ-like). Together they form the universal cover ℕ → Z/4.
--
-- Per the 2-D word algebra arc: instance #2 (n=4). Demonstrates that
-- the 2-D structure construction is mechanical at any n.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Groups.Z4-x-FreeCyclic where

import Substrate.Groups.Z4-Coxeter as Z₄
import Substrate.Groups.FreeCyclic-Coxeter as F

------------------------------------------------------------------------
-- Instantiate DirectProduct: phase = Z₄, cycle = FreeCyclic.
------------------------------------------------------------------------

open import Substrate.Groups.Coxeter.DirectProduct
  -- Phase component: Z₄-Coxeter.
  (Z₄.Word Z₄.Gen) (Z₄._++_) Z₄.ε Z₄.++-assoc
    Z₄.Canonical Z₄.normalize Z₄.normalize-canonical
    Z₄.canonical-is-fixed-Z4 Z₄.normalize-distrib
  -- Cycle component: FreeCyclic-Coxeter.
  (F.Word F.Gen) (F._++_) F.ε F.++-assoc
    F.Canonical F.normalize F.normalize-canonical
    F.canonical-is-fixed-Free F.normalize-distrib
  public
