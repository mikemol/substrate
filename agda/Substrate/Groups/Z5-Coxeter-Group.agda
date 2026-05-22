------------------------------------------------------------------------
-- Substrate.Groups.Z5-Coxeter-Group
--
-- Z5-Coxeter as Group bundle — thin instance via the FromCapability
-- adapter + cap-Z₅ from Substrate.Groups.Capabilities.CoxeterGroup.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Groups.Z5-Coxeter-Group where

import Substrate.Groups.Z5-Coxeter as Z₅
open import Substrate.Groups.Capabilities.CoxeterGroup using (cap-Z₅)
open import Substrate.Groups.Coxeter.GroupFromCapability cap-Z₅ public

open Z₅ public using (Gen; a; c-ε; c-a; c-aa; c-aaa; c-aaaa)
