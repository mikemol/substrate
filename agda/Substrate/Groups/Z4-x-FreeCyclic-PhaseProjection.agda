------------------------------------------------------------------------
-- Substrate.Groups.Z4-x-FreeCyclic-PhaseProjection
--
-- The phase projection from the 2-D word algebra Z₄ × ℕ back to Z₄
-- as a thin instance of Substrate.Groups.Zn-x-FreeCyclic-PhaseProjection.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Groups.Z4-x-FreeCyclic-PhaseProjection where

import Substrate.Groups.Z4-Coxeter as Z₄
import Substrate.Groups.FreeCyclic-Coxeter as F

open import Substrate.Groups.Zn-x-FreeCyclic-PhaseProjection
  (Z₄.Word Z₄.Gen) Z₄.ε Z₄._++_ Z₄.normalize
  (F.Word F.Gen)   F.ε  F._++_  F.normalize
  public
