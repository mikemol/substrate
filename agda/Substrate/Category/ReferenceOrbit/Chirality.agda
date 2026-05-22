------------------------------------------------------------------------
-- Substrate.Category.ReferenceOrbit.Chirality
--
-- chirality-of : ReferenceOrbit → BindingClass.
-- Projects the chirality (substrate-aligned ↔ structure-agnostic)
-- coordinate from an orbit. Per [[3plus1-parity-universal]] this
-- is the "1" of the 3+1 split at the reference-generator level.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Category.ReferenceOrbit.Chirality where

open import Substrate.Category.ReferenceOrbit.BindingClass using (BindingClass)
open import Substrate.Category.ReferenceOrbit.Record using (ReferenceOrbit; binding)

chirality-of : ReferenceOrbit → BindingClass
chirality-of o = binding o
