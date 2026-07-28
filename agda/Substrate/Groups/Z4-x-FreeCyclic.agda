------------------------------------------------------------------------
-- Substrate.Groups.Z4-x-FreeCyclic
--
-- 2-D word algebra Z₄ × ℕ — thin instance via the FromCapability
-- adapter + cap-Z₄ from Substrate.Groups.Capabilities.xFreeCyclic.Witness (applied).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Groups.Z4-x-FreeCyclic where

import Substrate.Groups.Capabilities.xFreeCyclic.Witness as xFreeCyclicW
cap-Z₄ = xFreeCyclicW.cap 3

open import Substrate.Groups.Coxeter.xFreeCyclicFromCapability cap-Z₄