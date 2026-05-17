------------------------------------------------------------------------
-- Substrate.Groups.Z3-Coxeter-Group
--
-- Lifts Substrate.Groups.Z3-Coxeter to a stdlib Group bundle via
-- the generic Substrate.Groups.Coxeter.GroupAdapter.
--
-- Z/3's inversion swaps [a] ↔ [a,a] (canonical form: a⁻¹ = a², (a²)⁻¹ = a).
-- The per-instance inv + 4 inversion-related lemmas live in
-- Substrate.Groups.Z3-Coxeter; this module just wires them into the
-- GroupAdapter signature.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Groups.Z3-Coxeter-Group where

import Substrate.Groups.Z3-Coxeter as Z₃
open import Substrate.Groups.Coxeter.Word
  using (Word; []; _++_; ++-identity-left; ++-identity-right)

------------------------------------------------------------------------
-- 1. Open GroupAdapter with Z/3's Core + inversion data.
------------------------------------------------------------------------

open import Substrate.Groups.Coxeter.GroupAdapter
  (Word Z₃.Gen)
  _++_
  []
  (λ a b c → Z₃.++-assoc a b c)
  Z₃.Canonical
  Z₃.c-ε
  Z₃.normalize
  Z₃.normalize-canonical
  Z₃.canonical-is-fixed-Z3
  Z₃.normalize-distrib
  ++-identity-left
  ++-identity-right
  Z₃.inv
  Z₃.inv-canonical
  Z₃.inv-left-canonical
  Z₃.inv-right-canonical
  public

------------------------------------------------------------------------
-- 2. Re-export the Z₃ generator and Canonical constructors.
------------------------------------------------------------------------

open Z₃ public using (Gen; a; c-ε; c-a; c-aa)
