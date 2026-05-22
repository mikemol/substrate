------------------------------------------------------------------------
-- Substrate.Groups.Z7-Coxeter-Strict2Monoid
--
-- Z₇-Coxeter as Strict2Monoid — thin instance via the FromCapability
-- adapter + cap-Z₇ from Substrate.Groups.Capabilities.Strict2Monoid.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Groups.Z7-Coxeter-Strict2Monoid where

open import Substrate.Groups.Capabilities.Strict2Monoid using (cap-Z₇)
open import Substrate.Groups.Coxeter.Strict2MonoidFromCapability cap-Z₇ public
