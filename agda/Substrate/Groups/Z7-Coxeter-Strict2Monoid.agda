------------------------------------------------------------------------
-- Substrate.Groups.Z7-Coxeter-Strict2Monoid
--
-- Z₇-Coxeter as Strict2Monoid — thin instance via the FromCapability
-- adapter + cap-Z₇ from Substrate.Groups.Capabilities.Strict2Monoid.Witness (applied).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Groups.Z7-Coxeter-Strict2Monoid where

import Substrate.Groups.Capabilities.Strict2Monoid.Witness as Strict2MonoidW
cap-Z₇ = Strict2MonoidW.cap 6

open import Substrate.Groups.Coxeter.Strict2MonoidFromCapability cap-Z₇