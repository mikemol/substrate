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
-- ⚑ WAS `open import …RuleAction.V4Compose using (_∘V_)` (Ⓑ2c).  `V4Compose` was
-- a one-line conduit — `open import Groups.V4.Operations using () renaming (_·₄_
-- to _∘V_) public` — so `_∘V_` was V₄'s `_·_` under a RuleAction spelling that
-- existed ONLY in that re-export.  A ban sweep stripped the `renaming` (it is a
-- forbidden construct) without rewiring here, which emptied the conduit and
-- broke this file: the request bound nothing and agda reported only a WARNING
-- (ModuleDoesntExport), so the failure surfaced seven lines down as
-- `NotInScope: ∘V`.  Same pathology as `S5Verdict` — a `using` naming what a
-- module does not export breaks far from its cause.
--
-- Binding `_·_` at its real home is the ban-compliant repair: the alias was the
-- banned construct, so the fix is to drop the alias, not to restore it.
open import Substrate.Groups.V4.Operations
open import Substrate.Category.RuleAction.ComposeAffine using (compose-affine)
open import Substrate.Category.RuleAction.ComposePatch using (compose-patch)
open import Substrate.Category.RuleAction.ComposeSpan using (compose-span)

compose : RuleAction → RuleAction → RuleAction
compose a b = record
  { residue       = residue a ·₄ residue b
  ; affine        = compose-affine (affine a) (affine b)
  ; f2-patch      = compose-patch (f2-patch a) (f2-patch b)
  ; span-coupling = compose-span (span-coupling a) (span-coupling b)
  }
