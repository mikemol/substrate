------------------------------------------------------------------------
-- Substrate.WitnessTower.LehmerTowerMorphism.Witness2
--
-- Defines: witness-2
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.WitnessTower.LehmerTowerMorphism; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.WitnessTower.LehmerTowerMorphism.Witness2 where

open import Substrate.Foundation.Nat.Nat
open import Substrate.Foundation.Fin.Fin
open import Substrate.Algebra.F2.F2
open import Substrate.Algebra.F2.PlusF
open import Substrate.WitnessTower.LehmerPath.Decode
open import Substrate.WitnessTower.LehmerPath.LehmerPath
open import Substrate.WitnessTower.TowerCocycleGraded
open import Substrate.Foundation.Eq
open import Substrate.WitnessTower.LehmerTowerMorphism.FinParity
open import Substrate.WitnessTower.LehmerTowerMorphism.L2


witness-2 : signF (decode (l₂ ◂ suc (suc zero))) ≡ (finParity {3} (suc (suc zero)) +F signF (decode l₂))
witness-2 = refl
