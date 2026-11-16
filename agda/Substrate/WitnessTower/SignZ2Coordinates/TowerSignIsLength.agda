------------------------------------------------------------------------
-- Substrate.WitnessTower.SignZ2Coordinates.TowerSignIsLength
--
-- Defines: tower-sign-is-length
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.WitnessTower.SignZ2Coordinates; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K --guardedness #-}

module Substrate.WitnessTower.SignZ2Coordinates.TowerSignIsLength where

open import Substrate.Foundation.Nat.Nat
open import Substrate.Algebra.F2.FromBool
open import Substrate.WitnessTower.Wedge.OrientationRigCatPermSign
open import Substrate.WitnessTower.Wedge.OrientationRigCatPermCoxeterGeneral.Properties
open import Substrate.WitnessTower.LehmerPath.Decode
open import Substrate.WitnessTower.LehmerPath.DecodeIsPerm
open import Substrate.WitnessTower.LehmerPath.LehmerPath
open import Substrate.WitnessTower.TowerCocycleGraded
open import Substrate.Foundation.Eq
open import Substrate.Foundation.Eq.Cong



-- and = the Coxeter-length guise (via sign-wd, over any derivation).
tower-sign-is-length : {n : ℕ} (l : LehmerPath n) →
  signF (decode l) ≡ bool→F₂ (signW (coxeter-complete (decode l) (decode-is-perm l)))
tower-sign-is-length l =
  cong bool→F₂ (sign-wd (coxeter-complete (decode l) (decode-is-perm l)))
