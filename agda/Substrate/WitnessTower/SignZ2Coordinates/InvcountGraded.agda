------------------------------------------------------------------------
-- Substrate.WitnessTower.SignZ2Coordinates.InvcountGraded
--
-- Defines: invcount-graded
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.WitnessTower.SignZ2Coordinates; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K --guardedness #-}

module Substrate.WitnessTower.SignZ2Coordinates.InvcountGraded where

open import Substrate.Foundation.Nat.Nat
open import Substrate.Foundation.Nat.Plus
open import Substrate.Foundation.Fin.Fin
open import Substrate.Foundation.Fin.To
open import Substrate.Algebra.Wedge.Graded
open import Substrate.Algebra.Wedge.Graded.Morphism
open import Substrate.WitnessTower.Enumerate
open import Substrate.WitnessTower.IsPermutation
open import Substrate.WitnessTower.LehmerPath.Decode
open import Substrate.WitnessTower.LehmerPath.DecodeIsPerm
open import Substrate.WitnessTower.Wedge.OrientationRigCatPermSignChirality
open import Substrate.WitnessTower.LehmerTowerMorphism.LehmerGraded
open import Substrate.Foundation.Eq
open import Substrate.Foundation.Eq.Trans
open import Substrate.Foundation.Eq.Sym
open import Substrate.Foundation.Eq.Cong
open import Substrate.Foundation.Eq.Cong2
open import Substrate.WitnessTower.SignZ2Coordinates.InvcountInsert
open import Substrate.WitnessTower.SignZ2Coordinates.NatTarget



-- ROUTE A as a genuine ℕ-graded morphism out of the Lehmer tower — inserting
-- digit p adds toℕ p inversions (invcount-insert). The universal count cocycle.
invcount-graded : GradedDivStrMorphism lehmer-graded ℕ⁺-target
invcount-graded = record
  { map-C          = λ l → invCount (decode l)
  ; map-R          = toℕ
  ; respects-recon = λ n l p → invcount-insert p (decode l) (decode-is-perm l)
  }
