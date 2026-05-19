------------------------------------------------------------------------
-- Substrate.Groups.Z3-Coxeter-Strict2Monoid
--
-- Z₃-Coxeter packaged as a Strict2Monoid via FromCoxeter.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Groups.Z3-Coxeter-Strict2Monoid where

import Substrate.Groups.Z3-Coxeter as Z₃
open import Substrate.Groups.Coxeter.Word
  using (Word; []; _++_; ++-identity-left; ++-identity-right)

open import Substrate.Category.Strict2Monoid.FromCoxeter
  (Word Z₃.Gen)
  _++_
  []
  (λ a b c → Z₃.++-assoc a b c)
  ++-identity-left
  ++-identity-right
  Z₃.normalize
  Z₃.normalize-distrib
  public
