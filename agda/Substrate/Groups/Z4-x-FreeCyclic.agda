------------------------------------------------------------------------
-- Substrate.Groups.Z4-x-FreeCyclic
--
-- 2-D word algebra Z₄ × ℕ — thin instance via the FromCapability
-- adapter + cap-Z₄ from Substrate.Groups.Capabilities.xFreeCyclic.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Groups.Z4-x-FreeCyclic where

open import Substrate.Groups.Capabilities.xFreeCyclic using (cap-Z₄)
open import Substrate.Groups.Coxeter.xFreeCyclicFromCapability cap-Z₄ public
