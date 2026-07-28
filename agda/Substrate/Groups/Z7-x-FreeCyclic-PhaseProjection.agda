------------------------------------------------------------------------
-- Substrate.Groups.Z7-x-FreeCyclic-PhaseProjection
--
-- Phase projection for Z₇ × ℕ — thin instance via the FromCapability
-- adapter + cap-Z₇ from Substrate.Groups.Capabilities.PhaseProjection.Witness (applied).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Groups.Z7-x-FreeCyclic-PhaseProjection where

import Substrate.Groups.Capabilities.PhaseProjection.Witness as PhaseProjectionW
cap-Z₇ = PhaseProjectionW.cap 6

open import Substrate.Groups.Coxeter.PhaseProjectionFromCapability cap-Z₇