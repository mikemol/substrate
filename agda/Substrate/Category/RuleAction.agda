------------------------------------------------------------------------
-- Substrate.Category.RuleAction
--
-- U-arc: the codec's RuleAction abstraction. A = V₄ × AffineProjection
-- × F₂Patch × SpanCoupling (the first three commute; SpanCoupling
-- does not, so the full product is a semi-direct product when the
-- span factor is engaged). File-per-lemma:
--
--   RuleAction.V4                — V₄ Klein-four data
--   RuleAction.V4Compose         — _∘V_ composition table
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

open import Substrate.Category.RuleAction.V4
open import Substrate.Category.RuleAction.V4Compose
open import Substrate.Category.RuleAction.AffineProjection
open import Substrate.Category.RuleAction.F2Patch
open import Substrate.Category.RuleAction.SpanCoupling
open import Substrate.Category.RuleAction.Record
open import Substrate.Category.RuleAction.ComposeAffine
open import Substrate.Category.RuleAction.ComposePatch
open import Substrate.Category.RuleAction.ComposeSpan
open import Substrate.Category.RuleAction.Compose
open import Substrate.Category.RuleAction.Laws