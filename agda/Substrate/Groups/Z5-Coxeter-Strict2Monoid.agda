------------------------------------------------------------------------
-- Substrate.Groups.Z5-Coxeter-Strict2Monoid
--
-- Z₅-Coxeter as Strict2Monoid — thin instance via the FromCapability
-- adapter + cap-Z₅ from Substrate.Groups.Capabilities.Strict2Monoid.Witness (applied).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Groups.Z5-Coxeter-Strict2Monoid where

import Substrate.Groups.Capabilities.Strict2Monoid.Witness as Strict2MonoidW
cap-Z₅ = Strict2MonoidW.cap 4

open import Substrate.Groups.Coxeter.Strict2MonoidFromCapability cap-Z₅