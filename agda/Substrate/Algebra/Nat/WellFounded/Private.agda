------------------------------------------------------------------------
-- Substrate.Algebra.Nat.WellFounded.Private
--
-- Defines: Private
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.Algebra.Nat.WellFounded; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.Nat.WellFounded.Private where

open import Substrate.Foundation.Nat.Le
open import Substrate.Foundation.Nat.Lt
open import Substrate.Foundation.Nat.Nat
open import Substrate.Foundation.WellFounded



-- Helper: extend an Acc for n to an Acc for suc n by induction on
-- the incoming y < suc n proof.
