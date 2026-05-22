------------------------------------------------------------------------
-- Substrate.Groups.Z4-Coxeter-Group
--
-- Lifts Substrate.Groups.Z4-Coxeter to a stdlib Group bundle via
-- the generic Substrate.Groups.Coxeter.GroupAdapter.
--
-- Z/4's inversion table:
--   inv []        = []
--   inv [a]       = [a,a,a]   (a⁻¹ = a³)
--   inv [a,a]     = [a,a]     (a² is its own inverse)
--   inv [a,a,a]   = [a]       ((a³)⁻¹ = a)
--
-- Mirror of Substrate.Groups.Z3-Coxeter-Group at n=4.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Groups.Z4-Coxeter-Group where

import Substrate.Groups.Z4-Coxeter as Z₄
open import Substrate.Groups.Coxeter.Word
  using (Word; []; _++_; ++-identity-left; ++-identity-right)

------------------------------------------------------------------------
-- 1. Open GroupAdapter with Z/4's Core + inversion data.
------------------------------------------------------------------------

open import Substrate.Groups.Coxeter.GroupAdapter
  (Word Z₄.Gen)
  _++_
  []
  (λ a b c → Z₄.++-assoc a b c)
  Z₄.Canonical
  Z₄.c-ε
  Z₄.normalize
  Z₄.normalize-canonical
  Z₄.canonical-is-fixed
  Z₄.normalize-distrib
  ++-identity-left
  ++-identity-right
  Z₄.inv
  Z₄.inv-canonical
  Z₄.inv-left-canonical
  Z₄.inv-right-canonical
  public

------------------------------------------------------------------------
-- 2. Re-export the Z₄ generator and Canonical constructors.
------------------------------------------------------------------------

open Z₄ public using (Gen; a; c-ε; c-a; c-aa; c-aaa)
