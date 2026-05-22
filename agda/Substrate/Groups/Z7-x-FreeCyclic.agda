------------------------------------------------------------------------
-- Substrate.Groups.Z7-x-FreeCyclic
--
-- 2-D word algebra Z₇ × ℕ — thin instance via the FromCapability
-- adapter + cap-Z₇ from Substrate.Groups.Capabilities.xFreeCyclic.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Groups.Z7-x-FreeCyclic where

open import Substrate.Groups.Capabilities.xFreeCyclic using (cap-Z₇)
open import Substrate.Groups.Coxeter.xFreeCyclicFromCapability cap-Z₇ public
