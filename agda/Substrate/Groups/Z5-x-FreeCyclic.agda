------------------------------------------------------------------------
-- Substrate.Groups.Z5-x-FreeCyclic
--
-- 2-D word algebra Z₅ × ℕ — thin instance via the FromCapability
-- adapter + cap-Z₅ from Substrate.Groups.Capabilities.xFreeCyclic.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Groups.Z5-x-FreeCyclic where

open import Substrate.Groups.Capabilities.xFreeCyclic using (cap-Z₅)
open import Substrate.Groups.Coxeter.xFreeCyclicFromCapability cap-Z₅ public
