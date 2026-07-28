------------------------------------------------------------------------
-- Substrate.Groups.Z4-x-FreeCyclic-PhaseProjection
--
-- Phase projection for Z₄ × ℕ — thin instance via the FromCapability
-- adapter + cap-Z₄ from Substrate.Groups.Capabilities.PhaseProjection.Witness (applied).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Groups.Z4-x-FreeCyclic-PhaseProjection where

import Substrate.Groups.Capabilities.PhaseProjection.Witness as PhaseProjectionW
cap-Z₄ = PhaseProjectionW.cap 3

open import Substrate.Groups.Coxeter.PhaseProjectionFromCapability cap-Z₄