------------------------------------------------------------------------
-- Substrate.Groups.Z7-Coxeter-Strict2Monoid
--
-- Z₇-Coxeter as Strict2Monoid — thin instantiation of the parametric
-- Zn-Coxeter-Strict2Monoid module.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Groups.Z7-Coxeter-Strict2Monoid where

import Substrate.Groups.Z7-Coxeter as Z₇
open import Substrate.Groups.Coxeter.Word
  using (Word; []; _++_; ++-identity-left; ++-identity-right)

open import Substrate.Groups.Zn-Coxeter-Strict2Monoid
  (Word Z₇.Gen) _++_ []
  (λ a b c → Z₇.++-assoc a b c)
  ++-identity-left ++-identity-right
  Z₇.normalize Z₇.normalize-distrib
  public
