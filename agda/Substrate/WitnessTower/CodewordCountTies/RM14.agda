------------------------------------------------------------------------
-- Substrate.WitnessTower.CodewordCountTies.RM14
--
-- Defines: RM-1-4
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.WitnessTower.CodewordCountTies; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.WitnessTower.CodewordCountTies.RM14 where

open import Substrate.Foundation.Nat.Nat
open import Substrate.Foundation.Nat.Pow
open import Substrate.Foundation.Bool.Bool
open import Substrate.Foundation.Eq
open import Substrate.Foundation.Eq.Trans
open import Substrate.Foundation.Eq.Cong2
open import Substrate.Category.ReedMullerHierarchy
open import Substrate.Foundation.Negation.Dec
open import Substrate.Foundation.Hedberg.DecidableUIP
open import Substrate.Foundation.Nat.Plus



------------------------------------------------------------------------
-- ◆AI-1c : the n=4 ceiling 2⁵ = 32 is RM(1,4)'s CODEWORD-COUNT (2^dimension).
------------------------------------------------------------------------


-- RM(1,4): order 1, dimension 4.
RM-1-4 : RMParams
RM-1-4 = record { m = 4 ; r = 1 }
