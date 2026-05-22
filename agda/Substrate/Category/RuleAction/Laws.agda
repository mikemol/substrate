------------------------------------------------------------------------
-- Substrate.Category.RuleAction.Laws
--
-- Action-law proof obligations (categorical "monoid action"):
--   LeftIdentity   : compose identity a ≡ a
--   RightIdentity  : compose a identity ≡ a
--   Associativity  : compose a (compose b c) ≡ compose (compose a b) c
--
-- Stated as types but not yet inhabited — proofs are mechanical
-- record-decomposition under positive sparsity, requiring V₄-action
-- infrastructure for the residue factor and case-analysis on
-- SpanCoupling.rule-right for the non-commutative associativity.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Category.RuleAction.Laws where

open import Substrate.Foundation.Eq using (_≡_)
open import Substrate.Category.RuleAction.Record using (RuleAction; identity)
open import Substrate.Category.RuleAction.Compose using (compose)

LeftIdentity  : Set
LeftIdentity  = ∀ (a : RuleAction) → compose identity a ≡ a

RightIdentity : Set
RightIdentity = ∀ (a : RuleAction) → compose a identity ≡ a

Associativity : Set
Associativity = ∀ (a b c : RuleAction) →
                  compose a (compose b c) ≡ compose (compose a b) c
