------------------------------------------------------------------------
-- Substrate.Groups.Z3-Coxeter-Strict2Monoid
--
-- Z₃-Coxeter as Strict2Monoid — thin instantiation of the parametric
-- Zn-Coxeter-Strict2Monoid module.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Groups.Z3-Coxeter-Strict2Monoid where

import Substrate.Groups.Z3-Coxeter as Z₃
open import Substrate.Groups.Coxeter.Word
  using (Word; []; _++_; ++-identity-left; ++-identity-right)

open import Substrate.Groups.Zn-Coxeter-Strict2Monoid
  (Word Z₃.Gen) _++_ []
  (λ a b c → Z₃.++-assoc a b c)
  ++-identity-left ++-identity-right
  Z₃.normalize Z₃.normalize-distrib
  public
