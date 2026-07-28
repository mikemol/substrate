------------------------------------------------------------------------
-- Substrate.Groups.Z3-Coxeter-Strict2Monoid
--
-- Z₃-Coxeter as Strict2Monoid — thin instance via the FromCapability
-- adapter + cap-Z₃ from Substrate.Groups.Capabilities.Strict2Monoid.Witness (applied).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Groups.Z3-Coxeter-Strict2Monoid where

import Substrate.Groups.Capabilities.Strict2Monoid.Witness as Strict2MonoidW
cap-Z₃ = Strict2MonoidW.cap 2

open import Substrate.Groups.Coxeter.Strict2MonoidFromCapability cap-Z₃