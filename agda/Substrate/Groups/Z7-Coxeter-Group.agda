------------------------------------------------------------------------
-- Substrate.Groups.Z7-Coxeter-Group
--
-- Lifts Substrate.Groups.Z7-Coxeter to a stdlib Group bundle via
-- the generic Substrate.Groups.Coxeter.GroupAdapter.
--
-- Mirror of Z₃/Z₄/Z₅-Coxeter-Group at n=7. Z/7 is prime-order cyclic
-- with no proper subgroups; inv : a ↦ a⁶, a² ↦ a⁵, a³ ↦ a⁴ (involution
-- on the cycle).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Groups.Z7-Coxeter-Group where

import Substrate.Groups.Z7-Coxeter as Z₇
open import Substrate.Groups.Coxeter.Word
  using (Word; []; _++_; ++-identity-left; ++-identity-right)

open import Substrate.Groups.Coxeter.GroupAdapter
  (Word Z₇.Gen)
  _++_
  []
  (λ a b c → Z₇.++-assoc a b c)
  Z₇.Canonical
  Z₇.c-ε
  Z₇.normalize
  Z₇.normalize-canonical
  Z₇.canonical-is-fixed-Z7
  Z₇.normalize-distrib
  ++-identity-left
  ++-identity-right
  Z₇.inv
  Z₇.inv-canonical
  Z₇.inv-left-canonical
  Z₇.inv-right-canonical
  public

open Z₇ public using (Gen; a; c-ε; c-a; c-aa; c-aaa; c-aaaa; c-aaaaa; c-aaaaaa)
