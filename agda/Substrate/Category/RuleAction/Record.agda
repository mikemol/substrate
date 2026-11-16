------------------------------------------------------------------------
-- Substrate.Category.RuleAction.Record
--
-- The RuleAction record:
--   A = V₄ × AffineProjection × F₂Patch × SpanCoupling.
-- Plus the identity element.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Category.RuleAction.Record where

open import Substrate.Groups.V4.Bijection.FromC
open import Substrate.Groups.V4.Bijection.FromCCanonical
open import Substrate.Groups.V4.Bijection.FromTo
open import Substrate.Groups.V4.Bijection.Private
open import Substrate.Groups.V4.Bijection.ToC
open import Substrate.Groups.V4.Bijection.ToCCanonical
open import Substrate.Groups.V4.Bijection.ToFromCanonical
open import Substrate.Groups.V4.Bijection.V4
open import Substrate.Category.RuleAction.AffineProjection
  using (AffineProjection; identity-affine)
open import Substrate.Category.RuleAction.F2Patch
  using (F₂Patch; identity-patch)
open import Substrate.Category.RuleAction.SpanCoupling
  using (SpanCoupling; identity-span)

record RuleAction : Set where
  field
    residue       : V₄
    affine        : AffineProjection
    f2-patch      : F₂Patch
    span-coupling : SpanCoupling

open RuleAction public

identity : RuleAction
identity = record
  { residue       = e
  ; affine        = identity-affine
  ; f2-patch      = identity-patch
  ; span-coupling = identity-span
  }
