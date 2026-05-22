------------------------------------------------------------------------
-- Substrate.Groups.Z2-Coxeter-Group
--
-- Z2-Coxeter as Group bundle — thin instance via the FromCapability
-- adapter + cap-Z₂ from Substrate.Groups.Capabilities.CoxeterGroup.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Groups.Z2-Coxeter-Group where

import Substrate.Groups.Z2-Coxeter as Z₂
open import Substrate.Groups.Capabilities.CoxeterGroup using (cap-Z₂)
open import Substrate.Groups.Coxeter.GroupFromCapability cap-Z₂ public

open Z₂ public using (Gen; a; c-ε; c-a)
