------------------------------------------------------------------------
-- Substrate.WitnessTower.CodewordCountTies.Rm16Dimension7
--
-- Defines: rm16-dimension-7
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.WitnessTower.CodewordCountTies; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.WitnessTower.CodewordCountTies.Rm16Dimension7 where

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
open import Substrate.WitnessTower.CodewordCountTies.RM16



rm16-dimension-7 : rm-dimension RM-1-6 ≡ 7
rm16-dimension-7 = refl
