------------------------------------------------------------------------
-- Substrate.WitnessTower.SignZ2Coordinates.SignTwoConstructionsAgree
--
-- Defines: sign-two-constructions-agree
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.WitnessTower.SignZ2Coordinates; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K --guardedness #-}

module Substrate.WitnessTower.SignZ2Coordinates.SignTwoConstructionsAgree where

open import Substrate.Foundation.Nat.Nat
open import Substrate.Algebra.N-to-F2-Parity
open import Substrate.Algebra.Wedge.Graded.Morphism
open import Substrate.WitnessTower.LehmerPath.Decode
open import Substrate.WitnessTower.LehmerPath.LehmerPath
open import Substrate.WitnessTower.TowerCocycleGraded
open import Substrate.WitnessTower.Wedge.OrientationRigCatPermSignChirality
open import Substrate.WitnessTower.LehmerTowerMorphism.F2Target
open import Substrate.WitnessTower.LehmerTowerMorphism.LehmerGraded
open import Substrate.WitnessTower.InsertionParity
open import Substrate.Foundation.Eq
open import Substrate.WitnessTower.SignZ2Coordinates.TowerSignIsInvcount
open import Substrate.WitnessTower.SignZ2Coordinates.SignLehmerViaInvcount



-- the two constructions of the twisted sign-morphism (Route B directly; Route A
-- through the ℕ count) AGREE on carriers — sign-as-parity, i.e. tower-sign-is-
-- invcount. Two graded morphisms, one F₂ cocycle: the content-cover route-
-- agreement wanted, now at the intermediate (count) level, not F₂-UIP.
sign-two-constructions-agree : {n : ℕ} (l : LehmerPath n) →
  map-C sign-lehmer-morphism-unconditional l ≡ map-C sign-lehmer-via-invcount l
sign-two-constructions-agree l = tower-sign-is-invcount l
