------------------------------------------------------------------------
-- Substrate.WitnessTower.SignZ2Coordinates.TowerSignIsInvcount
--
-- Defines: tower-sign-is-invcount
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.WitnessTower.SignZ2Coordinates; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K --guardedness #-}

module Substrate.WitnessTower.SignZ2Coordinates.TowerSignIsInvcount where

open import Substrate.Foundation.Nat.Nat
open import Substrate.Algebra.N-to-F2-Parity
open import Substrate.WitnessTower.LehmerPath.Decode
open import Substrate.WitnessTower.LehmerPath.LehmerPath
open import Substrate.WitnessTower.TowerCocycleGraded
open import Substrate.WitnessTower.Wedge.OrientationRigCatPermSignChirality
open import Substrate.Foundation.Eq



------------------------------------------------------------------------
-- ◆ip-chirality-coapex — the graded coordinate meets the static guises.
------------------------------------------------------------------------

-- the tower sign morphism's value at l = the inversion-count guise (Chirality:5).
tower-sign-is-invcount : {n : ℕ} (l : LehmerPath n) →
                         signF (decode l) ≡ parity (invCount (decode l))
tower-sign-is-invcount l = sign-as-parity (decode l)
