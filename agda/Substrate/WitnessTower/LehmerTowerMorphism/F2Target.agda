------------------------------------------------------------------------
-- Substrate.WitnessTower.LehmerTowerMorphism.F2Target
--
-- Defines: F₂-target
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.WitnessTower.LehmerTowerMorphism; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.WitnessTower.LehmerTowerMorphism.F2Target where

open import Substrate.Foundation.Nat.Nat
open import Substrate.Foundation.Fin.Fin
open import Substrate.Algebra.F2.F2
open import Substrate.Algebra.F2.PlusF
open import Substrate.WitnessTower.LehmerPath.Decode
open import Substrate.WitnessTower.LehmerPath.LehmerPath
open import Substrate.Algebra.Wedge.Graded
open import Substrate.Foundation.Eq



------------------------------------------------------------------------
-- the F₂ target: grade-additive recon (r +F b), the sign cocycle's home.
------------------------------------------------------------------------

F₂-target : GradedDivStr (λ _ → F₂) (λ _ → F₂)
F₂-target = record { recon = λ n b r → r +F b }
