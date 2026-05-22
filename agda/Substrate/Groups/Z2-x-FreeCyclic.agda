------------------------------------------------------------------------
-- Substrate.Groups.Z2-x-FreeCyclic
--
-- 2-D word algebra Z₂ × ℕ — thin instance via the FromCapability
-- adapter + cap-Z₂ from Substrate.Groups.Capabilities.xFreeCyclic.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Groups.Z2-x-FreeCyclic where

open import Substrate.Groups.Capabilities.xFreeCyclic using (cap-Z₂)
open import Substrate.Groups.Coxeter.xFreeCyclicFromCapability cap-Z₂ public
