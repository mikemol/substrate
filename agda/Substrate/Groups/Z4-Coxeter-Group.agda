------------------------------------------------------------------------
-- Substrate.Groups.Z4-Coxeter-Group
--
-- Z4-Coxeter as Group bundle — thin instance via the FromCapability
-- adapter + cap-Z₄ from Substrate.Groups.Capabilities.CoxeterGroup.Witness (applied).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Groups.Z4-Coxeter-Group where

import Substrate.Groups.Z4-Coxeter as Z₄
import Substrate.Groups.Capabilities.CoxeterGroup.Witness as CoxeterGroupW
open Z₄ public using (Gen; a; c-pos)
cap-Z₄ = CoxeterGroupW.cap 3


open import Substrate.Groups.Coxeter.GroupFromCapability cap-Z₄