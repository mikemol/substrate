------------------------------------------------------------------------
-- Substrate.WitnessTower.LehmerTowerMorphism.DecodeMorphism
--
-- Defines: decode-morphism
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.WitnessTower.LehmerTowerMorphism; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.WitnessTower.LehmerTowerMorphism.DecodeMorphism where

open import Substrate.Foundation.Nat.Nat
open import Substrate.Foundation.Fin.Fin
open import Substrate.Algebra.F2.F2
open import Substrate.Algebra.F2.PlusF
open import Substrate.WitnessTower.LehmerPath.Decode
open import Substrate.WitnessTower.LehmerPath.LehmerPath
open import Substrate.WitnessTower.Enumerate
open import Substrate.Algebra.Wedge.Graded
open import Substrate.WitnessTower.Wedge.Graded
open import Substrate.Algebra.Wedge.Graded.Morphism
open import Substrate.Foundation.Eq
open import Substrate.WitnessTower.LehmerTowerMorphism.LehmerGraded



------------------------------------------------------------------------
-- (2) THE PROVEN CORE: decode is a graded morphism lehmer-graded → tower-graded.
-- map-C = decode, map-R = id, respects-recon = refl (decode (l ◂ p) = insert-at
-- p (decode l) definitionally). The reorder-history tower maps to the perm
-- tower by a graded morphism, no twist needed at THIS level — the recon shapes
-- match on the nose.
------------------------------------------------------------------------

decode-morphism : GradedDivStrMorphism lehmer-graded tower-graded
decode-morphism = record
  { map-C          = decode
  ; map-R          = λ p → p
  ; respects-recon = λ n l p → refl
  }
