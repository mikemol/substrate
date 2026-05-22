------------------------------------------------------------------------
-- Substrate.Category.RuleAction.Compose
--
-- compose : the full RuleAction composition. Componentwise on the
-- first three factors; non-commutative compose-span on the fourth.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Category.RuleAction.Compose where

open import Substrate.Category.RuleAction.Record
  using (RuleAction; residue; affine; f2-patch; span-coupling)
open import Substrate.Category.RuleAction.V4Compose using (_∘V_)
open import Substrate.Category.RuleAction.ComposeAffine using (compose-affine)
open import Substrate.Category.RuleAction.ComposePatch using (compose-patch)
open import Substrate.Category.RuleAction.ComposeSpan using (compose-span)

compose : RuleAction → RuleAction → RuleAction
compose a b = record
  { residue       = residue a ∘V residue b
  ; affine        = compose-affine (affine a) (affine b)
  ; f2-patch      = compose-patch (f2-patch a) (f2-patch b)
  ; span-coupling = compose-span (span-coupling a) (span-coupling b)
  }
