------------------------------------------------------------------------
-- Substrate.Groups.Z2-x-FreeCyclic-PhaseProjection
--
-- Phase projection for Z₂ × ℕ — thin instance via the FromCapability
-- adapter + cap-Z₂ from Substrate.Groups.Capabilities.PhaseProjection.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Groups.Z2-x-FreeCyclic-PhaseProjection where

open import Substrate.Groups.Capabilities.PhaseProjection using (cap-Z₂)
open import Substrate.Groups.Coxeter.PhaseProjectionFromCapability cap-Z₂ public
