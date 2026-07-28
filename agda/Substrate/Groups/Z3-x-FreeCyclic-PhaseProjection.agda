------------------------------------------------------------------------
-- Substrate.Groups.Z3-x-FreeCyclic-PhaseProjection
--
-- Phase projection for Z₃ × ℕ — thin instance via the FromCapability
-- adapter + cap-Z₃ from Substrate.Groups.Capabilities.PhaseProjection.Witness (applied).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Groups.Z3-x-FreeCyclic-PhaseProjection where

import Substrate.Groups.Capabilities.PhaseProjection.Witness as PhaseProjectionW
cap-Z₃ = PhaseProjectionW.cap 2

open import Substrate.Groups.Coxeter.PhaseProjectionFromCapability cap-Z₃