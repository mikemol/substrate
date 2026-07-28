------------------------------------------------------------------------
-- Substrate.Groups.Z7-Coxeter-Group
--
-- Z7-Coxeter as Group bundle — thin instance via the FromCapability
-- adapter + cap-Z₇ from Substrate.Groups.Capabilities.CoxeterGroup.Witness (applied).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Groups.Z7-Coxeter-Group where

import Substrate.Groups.Z7-Coxeter as Z₇
import Substrate.Groups.Capabilities.CoxeterGroup.Witness as CoxeterGroupW
open Z₇ public using (Gen; a; c-pos)
cap-Z₇ = CoxeterGroupW.cap 6


open import Substrate.Groups.Coxeter.GroupFromCapability cap-Z₇