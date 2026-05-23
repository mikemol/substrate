------------------------------------------------------------------------
-- Substrate.Groups.Z7-Coxeter-Group
--
-- Z7-Coxeter as Group bundle — thin instance via the FromCapability
-- adapter + cap-Z₇ from Substrate.Groups.Capabilities.CoxeterGroup.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Groups.Z7-Coxeter-Group where

import Substrate.Groups.Z7-Coxeter as Z₇
open import Substrate.Groups.Capabilities.CoxeterGroup using (cap-Z₇)
open import Substrate.Groups.Coxeter.GroupFromCapability cap-Z₇ public

open Z₇ public using (Gen; a; c-pos)
