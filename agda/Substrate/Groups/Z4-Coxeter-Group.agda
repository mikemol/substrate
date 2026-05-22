------------------------------------------------------------------------
-- Substrate.Groups.Z4-Coxeter-Group
--
-- Z4-Coxeter as Group bundle — thin instance via the FromCapability
-- adapter + cap-Z₄ from Substrate.Groups.Capabilities.CoxeterGroup.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Groups.Z4-Coxeter-Group where

import Substrate.Groups.Z4-Coxeter as Z₄
open import Substrate.Groups.Capabilities.CoxeterGroup using (cap-Z₄)
open import Substrate.Groups.Coxeter.GroupFromCapability cap-Z₄ public

open Z₄ public using (Gen; a; c-ε; c-a; c-aa; c-aaa)
