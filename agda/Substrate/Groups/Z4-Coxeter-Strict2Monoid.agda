------------------------------------------------------------------------
-- Substrate.Groups.Z4-Coxeter-Strict2Monoid
--
-- Z₄-Coxeter as Strict2Monoid — thin instance via the FromCapability
-- adapter + cap-Z₄ from Substrate.Groups.Capabilities.Strict2Monoid.Witness (applied).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Groups.Z4-Coxeter-Strict2Monoid where

import Substrate.Groups.Capabilities.Strict2Monoid.Witness as Strict2MonoidW
cap-Z₄ = Strict2MonoidW.cap 3

open import Substrate.Groups.Coxeter.Strict2MonoidFromCapability cap-Z₄