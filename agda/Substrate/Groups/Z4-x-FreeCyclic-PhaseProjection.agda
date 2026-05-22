------------------------------------------------------------------------
-- Substrate.Groups.Z4-x-FreeCyclic-PhaseProjection
--
-- Phase projection for Z₄ × ℕ — thin instance via the FromCapability
-- adapter + cap-Z₄ from Substrate.Groups.Capabilities.PhaseProjection.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Groups.Z4-x-FreeCyclic-PhaseProjection where

open import Substrate.Groups.Capabilities.PhaseProjection using (cap-Z₄)
open import Substrate.Groups.Coxeter.PhaseProjectionFromCapability cap-Z₄ public
