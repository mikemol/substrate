------------------------------------------------------------------------
-- Substrate.Groups.Z2-Coxeter-Group
--
-- Z2-Coxeter as Group bundle — thin instance via the FromCapability
-- adapter + cap-Z₂ from Substrate.Groups.Capabilities.CoxeterGroup.Witness (applied).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Groups.Z2-Coxeter-Group where


import Substrate.Groups.Capabilities.CoxeterGroup.Witness as CoxeterGroupW
open import Substrate.Groups.Coxeter.Cyclic.Base 1 using (Gen)
cap-Z₂ = CoxeterGroupW.cap 1


open import Substrate.Groups.Coxeter.GroupFromCapability cap-Z₂