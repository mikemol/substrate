------------------------------------------------------------------------
-- Substrate.Groups.Z5-Coxeter-Strict2Monoid
--
-- Z₅-Coxeter as Strict2Monoid — thin instance via the FromCapability
-- adapter + cap-Z₅ from Substrate.Groups.Capabilities.Strict2Monoid.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Groups.Z5-Coxeter-Strict2Monoid where

open import Substrate.Groups.Capabilities.Strict2Monoid using (cap-Z₅)
open import Substrate.Groups.Coxeter.Strict2MonoidFromCapability cap-Z₅ public
