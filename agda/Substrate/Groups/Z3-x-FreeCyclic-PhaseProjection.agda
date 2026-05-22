------------------------------------------------------------------------
-- Substrate.Groups.Z3-x-FreeCyclic-PhaseProjection
--
-- The phase projection from the 2-D word algebra Z₃ × ℕ back to Z₃
-- as a thin instance of Substrate.Groups.Zn-x-FreeCyclic-PhaseProjection.
--
-- Per [[expose-generator-not-orbit]]: the chain `phase-project +
-- 3-refl homomorphism` was an orbit across Z₃/Z₄/Z₅; the generic IS
-- the chain.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Groups.Z3-x-FreeCyclic-PhaseProjection where

import Substrate.Groups.Z3-Coxeter as Z₃
import Substrate.Groups.FreeCyclic-Coxeter as F

open import Substrate.Groups.Zn-x-FreeCyclic-PhaseProjection
  (Z₃.Word Z₃.Gen) Z₃.ε Z₃._++_ Z₃.normalize
  (F.Word F.Gen)   F.ε  F._++_  F.normalize
  public
