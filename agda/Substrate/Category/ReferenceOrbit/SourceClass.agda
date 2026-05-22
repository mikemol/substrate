------------------------------------------------------------------------
-- Substrate.Category.ReferenceOrbit.SourceClass
--
-- The first axis: source-class distinction between
-- existing-rule-slice references (QUOT-style) and arbitrary-recent-
-- span references (LZ77-style).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Category.ReferenceOrbit.SourceClass where

data SourceClass : Set where
  ExistingRuleSlice    : SourceClass
  ArbitraryRecentSpan  : SourceClass
