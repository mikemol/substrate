------------------------------------------------------------------------
-- Substrate.Groups.Z3-x-FreeCyclic-PhaseProjection
--
-- Phase projection for Z₃ × ℕ — thin instance via the FromCapability
-- adapter + cap-Z₃ from Substrate.Groups.Capabilities.PhaseProjection.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Groups.Z3-x-FreeCyclic-PhaseProjection where

open import Substrate.Groups.Capabilities.PhaseProjection using (cap-Z₃)
open import Substrate.Groups.Coxeter.PhaseProjectionFromCapability cap-Z₃ public
