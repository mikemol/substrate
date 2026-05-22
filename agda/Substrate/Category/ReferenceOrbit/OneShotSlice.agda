------------------------------------------------------------------------
-- Substrate.Category.ReferenceOrbit.OneShotSlice
--
-- One-shot reference to an existing rule's slice. Cheaper than QUOT (no rule growth) but still chamber-state-bound.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Category.ReferenceOrbit.OneShotSlice where

open import Substrate.Category.ReferenceOrbit.SourceClass using (ExistingRuleSlice)
open import Substrate.Category.ReferenceOrbit.Permanence using (OneShot)
open import Substrate.Category.ReferenceOrbit.BindingClass using (ChamberBound)
open import Substrate.Category.ReferenceOrbit.Record using (ReferenceOrbit)

OneShotSlice : ReferenceOrbit
OneShotSlice = record
  { source = ExistingRuleSlice
  ; permanence = OneShot
  ; binding = ChamberBound
  }
