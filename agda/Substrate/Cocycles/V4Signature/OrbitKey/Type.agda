------------------------------------------------------------------------
-- Substrate.Cocycles.V4Signature.OrbitKey.Type
--
-- OrbitKey = Pairing × Chirality (6 elements). The invariant of the
-- CY-5 V₄-signature cocycle.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Cocycles.V4Signature.OrbitKey.Type where

open import Substrate.Foundation.Product using (_×_)
open import Substrate.Cocycles.V4Signature.Pairing.Type   using (Pairing)
open import Substrate.Cocycles.V4Signature.Chirality.Type using (Chirality)

OrbitKey : Set
OrbitKey = Pairing × Chirality
