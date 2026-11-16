------------------------------------------------------------------------
-- Substrate.Category.UniversalProperty.Instances.FreeMonoidUP
--
-- Defines: FreeMonoid-UP
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.Category.UniversalProperty.Instances; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Category.UniversalProperty.Instances.FreeMonoidUP where

open import Substrate.Foundation.Nat.Nat
open import Substrate.Foundation.Unit
open import Substrate.Foundation.Empty.Bot
open import Substrate.Foundation.Fin.Fin
open import Substrate.Category.FreeUniversalProperty
open import Substrate.Category.FreeUniversalProperty.FreeMonoid
open import Substrate.Foundation.Eq



------------------------------------------------------------------------
-- 1. FreeMonoid — Coxeter.Word ⊤ is the free monoid (extend = fold).
------------------------------------------------------------------------

FreeMonoid-UP = FreeUP-UPArrow (word-unit ⊤) ℕ
