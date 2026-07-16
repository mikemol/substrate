------------------------------------------------------------------------
-- Substrate.Groups.Z3-x-FreeCyclic-Strict2Monoid
--
-- The 2-D word algebra Z₃ × ℕ as a Strict2Monoid via the
-- Strict2Monoid.DirectProduct combinator on the Z₃ and FreeCyclic
-- Strict2Monoid instances.
--
-- This demonstrates the cleanest composition: existing Strict2Monoid
-- instances (Z₃ and FreeCyclic) combine via the categorical
-- DirectProduct combinator to give the 2-D Strict2Monoid for free.
-- Mirrors what Substrate.Groups.Z3-x-FreeCyclic does at the Coxeter
-- Core level.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Groups.Z3-x-FreeCyclic-Strict2Monoid where

open import Substrate.Category.Strict2Monoid using (Strict2Monoid)
open import Substrate.Category.Strict2Monoid.DirectProduct using (direct-product)

import Substrate.Groups.Z3-Coxeter-Strict2Monoid as Z₃-S2M
import Substrate.Groups.FreeCyclic-Coxeter-Strict2Monoid as F-S2M

------------------------------------------------------------------------
-- The DirectProduct instance.
--
-- Z₃-S2M.Coxeter-Strict2Monoid (the Strict2Monoid from Z₃-Coxeter) ×
-- F-S2M.Coxeter-Strict2Monoid (the Strict2Monoid from FreeCyclic) =
-- the 2-D Strict2Monoid for Z₃ × ℕ.
------------------------------------------------------------------------

Z3-x-F-Strict2Monoid : Strict2Monoid _ _ _ _
Z3-x-F-Strict2Monoid =
  direct-product Z₃-S2M.Coxeter-Strict2Monoid F-S2M.Coxeter-Strict2Monoid
