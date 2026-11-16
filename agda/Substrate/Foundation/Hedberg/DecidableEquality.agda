------------------------------------------------------------------------
-- Substrate.Foundation.Hedberg.DecidableEquality
--
-- Defines: DecidableEquality
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.Foundation.Hedberg; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Foundation.Hedberg.DecidableEquality where

open import Substrate.Foundation.Negation.Dec
open import Substrate.Foundation.Negation.DecNot
open import Substrate.Foundation.Negation.FromNotNot
open import Substrate.Foundation.Negation.Not
open import Substrate.Foundation.Negation.Preamble
open import Substrate.Foundation.Eq



------------------------------------------------------------------------
-- DecidableEquality.
------------------------------------------------------------------------

DecidableEquality : Set → Set
DecidableEquality A = (x y : A) → Dec (x ≡ y)
