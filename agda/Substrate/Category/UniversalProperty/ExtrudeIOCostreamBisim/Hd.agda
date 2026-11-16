------------------------------------------------------------------------
-- Substrate.Category.UniversalProperty.ExtrudeIOCostreamBisim.Hd
--
-- Defines: hd
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.Category.UniversalProperty.ExtrudeIOCostreamBisim; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K --guardedness #-}

module Substrate.Category.UniversalProperty.ExtrudeIOCostreamBisim.Hd where

open import Substrate.Foundation.Nat.Nat
open import Substrate.Foundation.List
open import Substrate.Category.UniversalProperty.ExtrudeIOCostream
open import Substrate.Foundation.Eq
open import Substrate.Foundation.Eq.Sym
open import Substrate.Foundation.Eq.Trans
open import Substrate.Foundation.Eq.Cong
open import Substrate.Foundation.Eq.Cong2
private variable O : Set
open import Substrate.Category.UniversalProperty.ExtrudeIOCostreamBisim.TakeCong



------------------------------------------------------------------------
-- ④ (⟡extrude-coio-bisim-complete) COMPLETENESS: equal on every finite prefix ⟹ bisimilar (the coinductive
--    limit — the converse of take-cong). Bisimilarity IS the "agrees on all observations" relation.
------------------------------------------------------------------------

hd : {O : Set} → O → List O → O
hd d []      = d
hd _ (x ∷ _) = x
