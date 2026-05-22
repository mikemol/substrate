------------------------------------------------------------------------
-- Substrate.Groups.Z5-x-FreeCyclic-PhaseProjection
--
-- The phase projection from the 2-D word algebra Z₅ × ℕ back to Z₅
-- as a thin instance of Substrate.Groups.Zn-x-FreeCyclic-PhaseProjection.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Groups.Z5-x-FreeCyclic-PhaseProjection where

import Substrate.Groups.Z5-Coxeter as Z₅
import Substrate.Groups.FreeCyclic-Coxeter as F

open import Substrate.Groups.Zn-x-FreeCyclic-PhaseProjection
  (Z₅.Word Z₅.Gen) Z₅.ε Z₅._++_ Z₅.normalize
  (F.Word F.Gen)   F.ε  F._++_  F.normalize
  public
