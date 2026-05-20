------------------------------------------------------------------------
-- Substrate.Groups.Z4-Coxeter-Strict2Monoid
--
-- Z₄-Coxeter as Strict2Monoid — thin instantiation of the parametric
-- Zn-Coxeter-Strict2Monoid module.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Groups.Z4-Coxeter-Strict2Monoid where

import Substrate.Groups.Z4-Coxeter as Z₄
open import Substrate.Groups.Coxeter.Word
  using (Word; []; _++_; ++-identity-left; ++-identity-right)

open import Substrate.Groups.Zn-Coxeter-Strict2Monoid
  (Word Z₄.Gen) _++_ []
  (λ a b c → Z₄.++-assoc a b c)
  ++-identity-left ++-identity-right
  Z₄.normalize Z₄.normalize-distrib
  public
