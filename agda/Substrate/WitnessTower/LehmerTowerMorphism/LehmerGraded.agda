------------------------------------------------------------------------
-- Substrate.WitnessTower.LehmerTowerMorphism.LehmerGraded
--
-- Defines: lehmer-graded
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.WitnessTower.LehmerTowerMorphism; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.WitnessTower.LehmerTowerMorphism.LehmerGraded where

open import Substrate.Foundation.Nat.Nat
open import Substrate.Foundation.Fin.Fin
open import Substrate.Algebra.F2.F2
open import Substrate.Algebra.F2.PlusF
open import Substrate.WitnessTower.LehmerPath.Decode
open import Substrate.WitnessTower.LehmerPath.LehmerPath
open import Substrate.Algebra.Wedge.Graded
open import Substrate.Foundation.Eq



------------------------------------------------------------------------
-- (1) the Lehmer tower as a graded div-structure. recon = _◂_ (append a digit).
------------------------------------------------------------------------

lehmer-graded : GradedDivStr LehmerPath (λ n → Fin (suc n))
lehmer-graded = record { recon = λ n l p → l ◂ p }
