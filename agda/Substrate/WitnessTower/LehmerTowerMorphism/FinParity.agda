------------------------------------------------------------------------
-- Substrate.WitnessTower.LehmerTowerMorphism.FinParity
--
-- Defines: finParity
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.WitnessTower.LehmerTowerMorphism; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.WitnessTower.LehmerTowerMorphism.FinParity where

open import Substrate.Foundation.Nat.Nat
open import Substrate.Foundation.Fin.Fin
open import Substrate.Algebra.F2.F2
open import Substrate.Algebra.F2.PlusF
open import Substrate.WitnessTower.LehmerPath.Decode
open import Substrate.WitnessTower.LehmerPath.LehmerPath
open import Substrate.Foundation.Eq



------------------------------------------------------------------------
-- the digit parity (the factoradic digit's contribution to the sign).
------------------------------------------------------------------------

finParity : {n : ℕ} → Fin n → F₂
finParity zero          = 𝟘
finParity (suc zero)    = 𝟙
finParity (suc (suc p)) = finParity p
