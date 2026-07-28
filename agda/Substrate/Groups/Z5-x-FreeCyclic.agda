------------------------------------------------------------------------
-- Substrate.Groups.Z5-x-FreeCyclic
--
-- 2-D word algebra Z₅ × ℕ — thin instance via the FromCapability
-- adapter + cap-Z₅ from Substrate.Groups.Capabilities.xFreeCyclic.Witness (applied).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Groups.Z5-x-FreeCyclic where

import Substrate.Groups.Capabilities.xFreeCyclic.Witness as xFreeCyclicW
cap-Z₅ = xFreeCyclicW.cap 4

open import Substrate.Groups.Coxeter.xFreeCyclicFromCapability cap-Z₅