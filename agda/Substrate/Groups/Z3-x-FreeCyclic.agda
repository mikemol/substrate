------------------------------------------------------------------------
-- Substrate.Groups.Z3-x-FreeCyclic
--
-- 2-D word algebra Z₃ × ℕ — thin instance via the FromCapability
-- adapter + cap-Z₃ from Substrate.Groups.Capabilities.xFreeCyclic.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Groups.Z3-x-FreeCyclic where

open import Substrate.Groups.Capabilities.xFreeCyclic using (cap-Z₃)
open import Substrate.Groups.Coxeter.xFreeCyclicFromCapability cap-Z₃ public
