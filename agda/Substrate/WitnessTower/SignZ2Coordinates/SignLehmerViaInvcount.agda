------------------------------------------------------------------------
-- Substrate.WitnessTower.SignZ2Coordinates.SignLehmerViaInvcount
--
-- Defines: sign-lehmer-via-invcount
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.WitnessTower.SignZ2Coordinates; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K --guardedness #-}

module Substrate.WitnessTower.SignZ2Coordinates.SignLehmerViaInvcount where

open import Substrate.Foundation.Fin.To
open import Substrate.Algebra.N-to-F2-Parity
open import Substrate.Algebra.Wedge.Graded.Morphism
open import Substrate.WitnessTower.LehmerPath.Decode
open import Substrate.WitnessTower.LehmerPath.DecodeIsPerm
open import Substrate.WitnessTower.Wedge.OrientationRigCatPermSignChirality
open import Substrate.WitnessTower.LehmerTowerMorphism.F2Target
open import Substrate.WitnessTower.LehmerTowerMorphism.LehmerGraded
open import Substrate.Foundation.Eq
open import Substrate.Foundation.Eq.Trans
open import Substrate.Foundation.Eq.Sym
open import Substrate.Foundation.Eq.Cong
open import Substrate.Foundation.Eq.Cong2
open import Substrate.WitnessTower.SignZ2Coordinates.InvcountGraded
open import Substrate.WitnessTower.SignZ2Coordinates.Mod2Graded



-- THE FACTORIZATION (◆ip-tower-f2-compose, dissolved through ℕ): the twisted F₂
-- sign-morphism is the mod-2 of the universal ℕ inversion-count morphism — a
-- SECOND construction of it, via comp-gdsm, distinct from Route B's sign-hom one.
sign-lehmer-via-invcount : GradedDivStrMorphism lehmer-graded F₂-target
sign-lehmer-via-invcount = comp-gdsm mod2-graded invcount-graded
