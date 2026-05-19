------------------------------------------------------------------------
-- Substrate.Groups.Z4-Coxeter-Strict2Monoid
--
-- Z₄-Coxeter packaged as a Strict2Monoid via FromCoxeter.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Groups.Z4-Coxeter-Strict2Monoid where

import Substrate.Groups.Z4-Coxeter as Z₄
open import Substrate.Groups.Coxeter.Word
  using (Word; []; _++_; ++-identity-left; ++-identity-right)

open import Substrate.Category.Strict2Monoid.FromCoxeter
  (Word Z₄.Gen)
  _++_
  []
  (λ a b c → Z₄.++-assoc a b c)
  ++-identity-left
  ++-identity-right
  Z₄.normalize
  Z₄.normalize-distrib
  public
