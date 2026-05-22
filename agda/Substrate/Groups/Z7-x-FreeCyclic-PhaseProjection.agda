------------------------------------------------------------------------
-- Substrate.Groups.Z7-x-FreeCyclic-PhaseProjection
--
-- Phase projection for Z₇ × ℕ — thin instance via the FromCapability
-- adapter + cap-Z₇ from Substrate.Groups.Capabilities.PhaseProjection.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Groups.Z7-x-FreeCyclic-PhaseProjection where

open import Substrate.Groups.Capabilities.PhaseProjection using (cap-Z₇)
open import Substrate.Groups.Coxeter.PhaseProjectionFromCapability cap-Z₇ public
