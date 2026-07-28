------------------------------------------------------------------------
-- Substrate.Groups.Z3-x-FreeCyclic
--
-- 2-D word algebra Z₃ × ℕ — thin instance via the FromCapability
-- adapter + cap-Z₃ from Substrate.Groups.Capabilities.xFreeCyclic.Witness (applied).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Groups.Z3-x-FreeCyclic where

import Substrate.Groups.Capabilities.xFreeCyclic.Witness as xFreeCyclicW
cap-Z₃ = xFreeCyclicW.cap 2

open import Substrate.Groups.Coxeter.xFreeCyclicFromCapability cap-Z₃