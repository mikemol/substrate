------------------------------------------------------------------------
-- Substrate.Groups.Z3-Coxeter-Strict2Monoid
--
-- Z₃-Coxeter as Strict2Monoid — thin instance via the FromCapability
-- adapter + cap-Z₃ from Substrate.Groups.Capabilities.Strict2Monoid.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Groups.Z3-Coxeter-Strict2Monoid where

open import Substrate.Groups.Capabilities.Strict2Monoid using (cap-Z₃)
open import Substrate.Groups.Coxeter.Strict2MonoidFromCapability cap-Z₃ public
