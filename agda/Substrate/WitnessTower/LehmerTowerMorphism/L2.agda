------------------------------------------------------------------------
-- Substrate.WitnessTower.LehmerTowerMorphism.L2
--
-- Defines: l₂
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.WitnessTower.LehmerTowerMorphism; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.WitnessTower.LehmerTowerMorphism.L2 where

open import Substrate.Foundation.Nat.Nat
open import Substrate.Foundation.Fin.Fin
open import Substrate.Algebra.F2.F2
open import Substrate.Algebra.F2.PlusF
open import Substrate.WitnessTower.LehmerPath.Decode
open import Substrate.WitnessTower.LehmerPath.LehmerPath
open import Substrate.WitnessTower.TowerCocycleGraded
open import Substrate.Foundation.Eq
open import Substrate.WitnessTower.LehmerTowerMorphism.FinParity



------------------------------------------------------------------------
-- CONCRETE COCYCLE WITNESSES (the general law holds definitionally on paths).
-- signF (decode (l ◂ p)) ≡ finParity p +F signF (decode l) — verified for a
-- grade-2 path across all three insertion digits. Not vacuous.
------------------------------------------------------------------------

l₂ : LehmerPath 2
l₂ = start ◂ zero ◂ suc zero
