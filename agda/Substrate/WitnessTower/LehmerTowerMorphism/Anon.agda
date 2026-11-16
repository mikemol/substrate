------------------------------------------------------------------------
-- Substrate.WitnessTower.LehmerTowerMorphism.Anon
--
-- Defines: _
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.WitnessTower.LehmerTowerMorphism; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.WitnessTower.LehmerTowerMorphism.Anon where

open import Substrate.Foundation.Nat.Nat
open import Substrate.Foundation.Fin.Fin
open import Substrate.Algebra.F2.F2
open import Substrate.Algebra.F2.PlusF
open import Substrate.WitnessTower.LehmerPath.Decode
open import Substrate.WitnessTower.LehmerPath.LehmerPath
open import Substrate.WitnessTower.TowerCocycleGraded
open import Substrate.Algebra.Wedge.Graded
open import Substrate.Algebra.Wedge.Graded.Morphism
open import Substrate.Foundation.Eq
open import Substrate.WitnessTower.LehmerTowerMorphism.LehmerGraded
open import Substrate.WitnessTower.LehmerTowerMorphism.FinParity
open import Substrate.WitnessTower.LehmerTowerMorphism.F2Target



------------------------------------------------------------------------
-- (3) THE FULL TWISTED SIGN-MORPHISM, conditional on the one open lemma. Given
-- the insertion-parity law (insertion-inversion-parity = digit parity on
-- decoded perms), signF ∘ decode is a GradedDivStrMorphism lehmer-graded →
-- F₂-target. The lemma is a module parameter — the obligation isolated, the
-- construction otherwise complete. (The witnesses above show the parameter is
-- satisfiable; a general proof needs the factoradic-digit ↔ inversion-count-
-- parity fact, the single open obligation of ◆AI-3-pkg-twisted-lehmer.)
------------------------------------------------------------------------

module _
  (insertion-parity :
    {n : ℕ} (l : LehmerPath n) (p : Fin (suc n)) →
    signF (decode (l ◂ p)) ≡ (finParity p +F signF (decode l)))
  where

  sign-lehmer-morphism : GradedDivStrMorphism lehmer-graded F₂-target
  sign-lehmer-morphism = record
    { map-C          = λ l → signF (decode l)
    ; map-R          = finParity
    ; respects-recon = λ n l p → insertion-parity l p
    }
