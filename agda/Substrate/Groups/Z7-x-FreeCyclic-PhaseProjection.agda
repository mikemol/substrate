------------------------------------------------------------------------
-- Substrate.Groups.Z7-x-FreeCyclic-PhaseProjection
--
-- Phase projection for Z₇ × ℕ — thin instance of
-- Substrate.Groups.Zn-x-FreeCyclic-PhaseProjection.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Groups.Z7-x-FreeCyclic-PhaseProjection where

import Substrate.Groups.Z7-Coxeter as Z₇
import Substrate.Groups.FreeCyclic-Coxeter as F

open import Substrate.Groups.Zn-x-FreeCyclic-PhaseProjection
  (Z₇.Word Z₇.Gen) Z₇.ε Z₇._++_ Z₇.normalize
  (F.Word F.Gen)   F.ε  F._++_  F.normalize
  public
