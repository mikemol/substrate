------------------------------------------------------------------------
-- Substrate.Groups.Z2-x-FreeCyclic-PhaseProjection
--
-- Phase projection for Z₂ × ℕ — thin instance via the FromCapability
-- adapter + cap-Z₂ from Substrate.Groups.Capabilities.PhaseProjection.Witness (applied).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Groups.Z2-x-FreeCyclic-PhaseProjection where

import Substrate.Groups.Capabilities.PhaseProjection.Witness as PhaseProjectionW
cap-Z₂ = PhaseProjectionW.cap 1

open import Substrate.Groups.Coxeter.PhaseProjectionFromCapability cap-Z₂