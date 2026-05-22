------------------------------------------------------------------------
-- Substrate.Groups.Z5-Coxeter-Group
--
-- Lifts Substrate.Groups.Z5-Coxeter to a stdlib Group bundle via
-- the generic Substrate.Groups.Coxeter.GroupAdapter.
--
-- Z/5's inversion table (prime-order cyclic, no proper subgroups):
--   inv []           = []
--   inv [a]          = [a,a,a,a]   (a⁻¹ = a⁴)
--   inv [a,a]        = [a,a,a]     ((a²)⁻¹ = a³)
--   inv [a,a,a]      = [a,a]       ((a³)⁻¹ = a²)
--   inv [a,a,a,a]    = [a]         ((a⁴)⁻¹ = a)
--
-- Mirror of Z3-Coxeter-Group and Z4-Coxeter-Group at n=5.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Groups.Z5-Coxeter-Group where

import Substrate.Groups.Z5-Coxeter as Z₅
open import Substrate.Groups.Coxeter.Word
  using (Word; []; _++_; ++-identity-left; ++-identity-right)

------------------------------------------------------------------------
-- 1. Open GroupAdapter with Z/5's Core + inversion data.
------------------------------------------------------------------------

open import Substrate.Groups.Coxeter.GroupAdapter
  (Word Z₅.Gen)
  _++_
  []
  (λ a b c → Z₅.++-assoc a b c)
  Z₅.Canonical
  Z₅.c-ε
  Z₅.normalize
  Z₅.normalize-canonical
  Z₅.canonical-is-fixed
  Z₅.normalize-distrib
  ++-identity-left
  ++-identity-right
  Z₅.inv
  Z₅.inv-canonical
  Z₅.inv-left-canonical
  Z₅.inv-right-canonical
  public

------------------------------------------------------------------------
-- 2. Re-export the Z₅ generator and Canonical constructors.
------------------------------------------------------------------------

open Z₅ public using (Gen; a; c-ε; c-a; c-aa; c-aaa; c-aaaa)
