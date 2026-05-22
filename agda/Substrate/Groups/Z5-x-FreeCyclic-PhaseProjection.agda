------------------------------------------------------------------------
-- Substrate.Groups.Z5-x-FreeCyclic-PhaseProjection
--
-- Phase projection for Z₅ × ℕ — thin instance via the FromCapability
-- adapter + cap-Z₅ from Substrate.Groups.Capabilities.PhaseProjection.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Groups.Z5-x-FreeCyclic-PhaseProjection where

open import Substrate.Groups.Capabilities.PhaseProjection using (cap-Z₅)
open import Substrate.Groups.Coxeter.PhaseProjectionFromCapability cap-Z₅ public
