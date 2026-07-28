------------------------------------------------------------------------
-- Substrate.Groups.Z5-Coxeter-Group
--
-- Z5-Coxeter as Group bundle — thin instance via the FromCapability
-- adapter + cap-Z₅ from Substrate.Groups.Capabilities.CoxeterGroup.Witness (applied).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Groups.Z5-Coxeter-Group where

import Substrate.Groups.Z5-Coxeter as Z₅
import Substrate.Groups.Capabilities.CoxeterGroup.Witness as CoxeterGroupW
open Z₅ public using (Gen; a; c-pos)
cap-Z₅ = CoxeterGroupW.cap 4


open import Substrate.Groups.Coxeter.GroupFromCapability cap-Z₅