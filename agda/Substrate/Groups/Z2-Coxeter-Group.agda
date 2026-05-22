------------------------------------------------------------------------
-- Substrate.Groups.Z2-Coxeter-Group
--
-- Lifts Substrate.Groups.Z2-Coxeter to a stdlib Group bundle via
-- the generic Substrate.Groups.Coxeter.GroupAdapter. Mirror of
-- Z3/Z4/Z5/Z7-Coxeter-Group; inv + cancellation lemmas live in
-- Z2-Coxeter (Z/2 elements are self-inverse).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Groups.Z2-Coxeter-Group where

import Substrate.Groups.Z2-Coxeter as Z₂
open import Substrate.Groups.Coxeter.Word
  using (Word; []; _++_; ++-identity-left; ++-identity-right)

open import Substrate.Groups.Coxeter.GroupAdapter
  (Word Z₂.Gen)
  _++_
  []
  (λ a b c → Z₂.++-assoc a b c)
  Z₂.Canonical
  Z₂.c-ε
  Z₂.normalize
  Z₂.normalize-canonical
  Z₂.canonical-is-fixed
  Z₂.normalize-distrib
  ++-identity-left
  ++-identity-right
  Z₂.inv
  Z₂.inv-canonical
  Z₂.inv-left-canonical
  Z₂.inv-right-canonical
  public

open Z₂ public using (Gen; a; c-ε; c-a)
