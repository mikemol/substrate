------------------------------------------------------------------------
-- Substrate.Groups.Z2-Coxeter-Strict2Monoid
--
-- Z₂-Coxeter as Strict2Monoid — thin instantiation of the parametric
-- Zn-Coxeter-Strict2Monoid module.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Groups.Z2-Coxeter-Strict2Monoid where

import Substrate.Groups.Z2-Coxeter as Z₂
open import Substrate.Groups.Coxeter.Word
  using (Word; []; _++_; ++-identity-left; ++-identity-right)

open import Substrate.Groups.Zn-Coxeter-Strict2Monoid
  (Word Z₂.Gen) _++_ []
  (λ a b c → Z₂.++-assoc a b c)
  ++-identity-left ++-identity-right
  Z₂.normalize Z₂.normalize-distrib
  public
