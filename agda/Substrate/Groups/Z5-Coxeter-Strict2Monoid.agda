------------------------------------------------------------------------
-- Substrate.Groups.Z5-Coxeter-Strict2Monoid
--
-- Z₅-Coxeter packaged as a Strict2Monoid via FromCoxeter.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Groups.Z5-Coxeter-Strict2Monoid where

import Substrate.Groups.Z5-Coxeter as Z₅
open import Substrate.Groups.Coxeter.Word
  using (Word; []; _++_; ++-identity-left; ++-identity-right)

open import Substrate.Category.Strict2Monoid.FromCoxeter
  (Word Z₅.Gen)
  _++_
  []
  (λ a b c → Z₅.++-assoc a b c)
  ++-identity-left
  ++-identity-right
  Z₅.normalize
  Z₅.normalize-distrib
  public
