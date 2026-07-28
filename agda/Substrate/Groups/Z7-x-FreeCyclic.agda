------------------------------------------------------------------------
-- Substrate.Groups.Z7-x-FreeCyclic
--
-- 2-D word algebra Z₇ × ℕ — thin instance via the FromCapability
-- adapter + cap-Z₇ from Substrate.Groups.Capabilities.xFreeCyclic.Witness (applied).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Groups.Z7-x-FreeCyclic where

import Substrate.Groups.Capabilities.xFreeCyclic.Witness as xFreeCyclicW
cap-Z₇ = xFreeCyclicW.cap 6

open import Substrate.Groups.Coxeter.xFreeCyclicFromCapability cap-Z₇