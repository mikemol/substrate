------------------------------------------------------------------------
-- Substrate.Groups.Z5-x-FreeCyclic-PhaseProjection
--
-- Phase projection for Z₅ × ℕ — thin instance via the FromCapability
-- adapter + cap-Z₅ from Substrate.Groups.Capabilities.PhaseProjection.Witness (applied).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Groups.Z5-x-FreeCyclic-PhaseProjection where

import Substrate.Groups.Capabilities.PhaseProjection.Witness as PhaseProjectionW
cap-Z₅ = PhaseProjectionW.cap 4

open import Substrate.Groups.Coxeter.PhaseProjectionFromCapability cap-Z₅