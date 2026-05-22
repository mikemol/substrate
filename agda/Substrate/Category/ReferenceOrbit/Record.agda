------------------------------------------------------------------------
-- Substrate.Category.ReferenceOrbit.Record
--
-- ReferenceOrbit: a point in the 2³ orbit space at the reference
-- generator. Fields: source / permanence / binding (one boolean
-- axis each).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Category.ReferenceOrbit.Record where

open import Substrate.Category.ReferenceOrbit.SourceClass using (SourceClass)
open import Substrate.Category.ReferenceOrbit.Permanence using (Permanence)
open import Substrate.Category.ReferenceOrbit.BindingClass using (BindingClass)

record ReferenceOrbit : Set where
  field
    source       : SourceClass
    permanence   : Permanence
    binding      : BindingClass

open ReferenceOrbit public
