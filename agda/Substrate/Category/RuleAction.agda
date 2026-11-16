------------------------------------------------------------------------
-- Substrate.Category.RuleAction
--
-- U-arc: the codec's RuleAction abstraction. A = V₄ × AffineProjection
-- × F₂Patch × SpanCoupling (the first three commute; SpanCoupling
-- does not, so the full product is a semi-direct product when the
-- span factor is engaged). File-per-lemma:
--
--   RuleAction.V4                — V₄ Klein-four data
-- ⚑ `RuleAction.V4Compose — _∘V_ composition table` RETIRED (Ⓑ2c).  It was never
-- a table: the module's whole body was `open import Groups.V4.Operations using ()
-- renaming (_·_ to _∘V_) public` — a re-export whose ONLY content was the alias,
-- and `renaming` + `public` are both banned constructs.  So `_∘V_` was V₄'s `_·_`
-- under a spelling that existed nowhere else.  `Compose` binds `_·_` at its real
-- home; dropping the alias IS the repair, since the alias was the violation.
--   RuleAction.AffineProjection  — record + identity-affine
--   RuleAction.F2Patch           — list-based F₂ patch + identity
--   RuleAction.SpanCoupling      — record + identity-span
--   RuleAction.Record            — RuleAction record + identity
--   RuleAction.ComposeAffine     — compose-affine
--   RuleAction.ComposePatch      — compose-patch
--   RuleAction.ComposeSpan       — compose-span (non-commutative)
--   RuleAction.Compose           — top-level compose
--   RuleAction.Laws              — LeftIdentity / RightIdentity /
--                                   Associativity (stated, not yet
--                                   discharged)
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Category.RuleAction where

open import Substrate.Groups.V4.Bijection.FromC
open import Substrate.Groups.V4.Bijection.FromCCanonical
open import Substrate.Groups.V4.Bijection.FromTo
open import Substrate.Groups.V4.Bijection.Private
open import Substrate.Groups.V4.Bijection.ToC
open import Substrate.Groups.V4.Bijection.ToCCanonical
open import Substrate.Groups.V4.Bijection.ToFromCanonical
open import Substrate.Groups.V4.Bijection.V4
open import Substrate.Category.RuleAction.AffineProjection
open import Substrate.Category.RuleAction.F2Patch
open import Substrate.Category.RuleAction.SpanCoupling
open import Substrate.Category.RuleAction.Record
open import Substrate.Category.RuleAction.ComposeAffine
open import Substrate.Category.RuleAction.ComposePatch
open import Substrate.Category.RuleAction.ComposeSpan
open import Substrate.Category.RuleAction.Compose
open import Substrate.Category.RuleAction.Laws