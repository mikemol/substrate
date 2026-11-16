------------------------------------------------------------------------
-- Substrate.Category.UniversalProperty.Instances.FreeModuleUP
--
-- Defines: FreeModule-UP
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.Category.UniversalProperty.Instances; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Category.UniversalProperty.Instances.FreeModuleUP where

open import Substrate.Foundation.Nat.Nat
open import Substrate.Foundation.Empty.Bot
open import Substrate.Foundation.Fin.Fin
open import Substrate.Category.FreeUniversalProperty
open import Substrate.Algebra.F2.Vector
open import Substrate.Foundation.Eq



------------------------------------------------------------------------
-- 2. FreeModule — Vector k is the free F₂-module on Fin k.
------------------------------------------------------------------------

FreeModule-UP = FreeUP-UPArrow (basis {n = 1}) ℕ
