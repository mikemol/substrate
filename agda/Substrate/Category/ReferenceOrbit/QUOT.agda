------------------------------------------------------------------------
-- Substrate.Category.ReferenceOrbit.QUOT
--
-- Alias-define orbit at substrate-aligned position. Existing rule's slice, permanently grows the rule table.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Category.ReferenceOrbit.QUOT where

open import Substrate.Category.ReferenceOrbit.SourceClass using (ExistingRuleSlice)
open import Substrate.Category.ReferenceOrbit.Permanence using (PermanentRule)
open import Substrate.Category.ReferenceOrbit.BindingClass using (ChamberBound)
open import Substrate.Category.ReferenceOrbit.Record using (ReferenceOrbit)

QUOT : ReferenceOrbit
QUOT = record
  { source = ExistingRuleSlice
  ; permanence = PermanentRule
  ; binding = ChamberBound
  }
