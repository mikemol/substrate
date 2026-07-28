------------------------------------------------------------------------
-- Substrate.Groups.FreeCyclic-Coxeter-Strict2Monoid
--
-- FreeCyclic-Coxeter packaged as a Strict2Monoid via FromCoxeter.
--
-- The "no relations" Coxeter instance also lifts to a Strict2Monoid;
-- its 2-cell relation is normalize-equality but since normalize is
-- identity, the 2-cells reduce to propositional equality on the
-- underlying words.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Groups.FreeCyclic-Coxeter-Strict2Monoid where
open import Substrate.Groups.Coxeter.Word using (++-assoc)

import Substrate.Groups.FreeCyclic-Coxeter as F
open import Substrate.Groups.Coxeter.Word
  using (Word; []; _++_; ++-identity-left; ++-identity-right)

open import Substrate.Category.Strict2Monoid.FromCoxeter
  (Word F.Gen)
  _++_
  []
  (λ a b c → ++-assoc a b c)
  ++-identity-left
  ++-identity-right
  F.normalize
  F.normalize-distrib
  public
