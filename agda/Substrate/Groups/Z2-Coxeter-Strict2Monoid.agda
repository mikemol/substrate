------------------------------------------------------------------------
-- Substrate.Groups.Z2-Coxeter-Strict2Monoid
--
-- Z₂-Coxeter as Strict2Monoid — thin instance via the FromCapability
-- adapter + cap-Z₂ from Substrate.Groups.Capabilities.Strict2Monoid.Witness (applied).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Groups.Z2-Coxeter-Strict2Monoid where

import Substrate.Groups.Capabilities.Strict2Monoid.Witness as Strict2MonoidW
cap-Z₂ = Strict2MonoidW.cap 1

open import Substrate.Groups.Coxeter.Strict2MonoidFromCapability cap-Z₂