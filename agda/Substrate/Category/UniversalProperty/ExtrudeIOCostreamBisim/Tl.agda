------------------------------------------------------------------------
-- Substrate.Category.UniversalProperty.ExtrudeIOCostreamBisim.Tl
--
-- Defines: tl
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.Category.UniversalProperty.ExtrudeIOCostreamBisim; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K --guardedness #-}

module Substrate.Category.UniversalProperty.ExtrudeIOCostreamBisim.Tl where

open import Substrate.Foundation.Nat.Nat
open import Substrate.Foundation.List
open import Substrate.Foundation.Eq
open import Substrate.Foundation.Eq.Sym
open import Substrate.Foundation.Eq.Trans
open import Substrate.Foundation.Eq.Cong
open import Substrate.Foundation.Eq.Cong2
private variable O : Set


tl : {O : Set} → List O → List O
tl []       = []
tl (_ ∷ xs) = xs
