------------------------------------------------------------------------
-- Substrate.Groups.Z3-Coxeter-Group
--
-- Z3-Coxeter as Group bundle — thin instance via the FromCapability
-- adapter + cap-Z₃ from Substrate.Groups.Capabilities.CoxeterGroup.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Groups.Z3-Coxeter-Group where

import Substrate.Groups.Z3-Coxeter as Z₃
open import Substrate.Groups.Capabilities.CoxeterGroup using (cap-Z₃)
open import Substrate.Groups.Coxeter.GroupFromCapability cap-Z₃ public

open Z₃ public using (Gen; a; c-ε; c-a; c-aa)
