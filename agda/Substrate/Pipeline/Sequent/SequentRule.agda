------------------------------------------------------------------------
-- Substrate.Pipeline.Sequent.SequentRule
--
-- The 6 structural rules of sequent calculus as a data tag:
-- identity / cut / weakening / contraction / exchange / coerce.
-- Used as the Sequent record's `rule` field (informational tag).
------------------------------------------------------------------------

{-# OPTIONS --without-K #-}

module Substrate.Pipeline.Sequent.SequentRule where

data SequentRule : Set where
  identity    : SequentRule
  cut         : SequentRule
  weakening   : SequentRule
  contraction : SequentRule
  exchange    : SequentRule
  coerce      : SequentRule
