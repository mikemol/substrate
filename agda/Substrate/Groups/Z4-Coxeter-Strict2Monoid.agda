------------------------------------------------------------------------
-- Substrate.Groups.Z4-Coxeter-Strict2Monoid
--
-- Z₄-Coxeter as Strict2Monoid — thin instance via the FromCapability
-- adapter + cap-Z₄ from Substrate.Groups.Capabilities.Strict2Monoid.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Groups.Z4-Coxeter-Strict2Monoid where

open import Substrate.Groups.Capabilities.Strict2Monoid using (cap-Z₄)
open import Substrate.Groups.Coxeter.Strict2MonoidFromCapability cap-Z₄ public
