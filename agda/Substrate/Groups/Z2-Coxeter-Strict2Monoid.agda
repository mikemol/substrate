------------------------------------------------------------------------
-- Substrate.Groups.Z2-Coxeter-Strict2Monoid
--
-- Z₂-Coxeter as Strict2Monoid — thin instance via the FromCapability
-- adapter + cap-Z₂ from Substrate.Groups.Capabilities.Strict2Monoid.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Groups.Z2-Coxeter-Strict2Monoid where

open import Substrate.Groups.Capabilities.Strict2Monoid using (cap-Z₂)
open import Substrate.Groups.Coxeter.Strict2MonoidFromCapability cap-Z₂ public
