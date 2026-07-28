------------------------------------------------------------------------
-- Substrate.Groups.Z2-x-FreeCyclic
--
-- 2-D word algebra Z₂ × ℕ — thin instance via the FromCapability
-- adapter + cap-Z₂ from Substrate.Groups.Capabilities.xFreeCyclic.Witness (applied).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Groups.Z2-x-FreeCyclic where

import Substrate.Groups.Capabilities.xFreeCyclic.Witness as xFreeCyclicW
cap-Z₂ = xFreeCyclicW.cap 1

open import Substrate.Groups.Coxeter.xFreeCyclicFromCapability cap-Z₂