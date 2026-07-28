------------------------------------------------------------------------
-- Substrate.Groups.Z3-Coxeter-Group
--
-- Z3-Coxeter as Group bundle — thin instance via the FromCapability
-- adapter + cap-Z₃ from Substrate.Groups.Capabilities.CoxeterGroup.Witness (applied).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Groups.Z3-Coxeter-Group where


import Substrate.Groups.Capabilities.CoxeterGroup.Witness as CoxeterGroupW
open import Substrate.Groups.Coxeter.Cyclic.Base 2 using (Gen)
cap-Z₃ = CoxeterGroupW.cap 2


open import Substrate.Groups.Coxeter.GroupFromCapability cap-Z₃