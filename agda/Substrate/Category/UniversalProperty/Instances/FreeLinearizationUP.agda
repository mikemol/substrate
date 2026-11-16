------------------------------------------------------------------------
-- Substrate.Category.UniversalProperty.Instances.FreeLinearizationUP
--
-- Defines: FreeLinearization-UP
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.Category.UniversalProperty.Instances; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Category.UniversalProperty.Instances.FreeLinearizationUP where

open import Substrate.Foundation.Nat.Nat
open import Substrate.Foundation.Empty.Bot
open import Substrate.Foundation.Fin.Fin
open import Substrate.Category.FreeUniversalProperty
open import Substrate.Algebra.F2.Vector
open import Substrate.Foundation.Eq



------------------------------------------------------------------------
-- 5. FreeLinearization — free linearization = the free F₂-module UP
--    (here dim 2; the dedicated FreeLinearization module is the same UP).
------------------------------------------------------------------------

FreeLinearization-UP = FreeUP-UPArrow (basis {n = 2}) ℕ
