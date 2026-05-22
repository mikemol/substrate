------------------------------------------------------------------------
-- Substrate.Groups.Z2-x-FreeCyclic-PhaseProjection
--
-- Phase projection for Z₂ × ℕ — thin instance of
-- Substrate.Groups.Zn-x-FreeCyclic-PhaseProjection.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Groups.Z2-x-FreeCyclic-PhaseProjection where

import Substrate.Groups.Z2-Coxeter as Z₂
import Substrate.Groups.FreeCyclic-Coxeter as F

open import Substrate.Groups.Zn-x-FreeCyclic-PhaseProjection
  (Z₂.Word Z₂.Gen) Z₂.ε Z₂._++_ Z₂.normalize
  (F.Word F.Gen)   F.ε  F._++_  F.normalize
  public
