------------------------------------------------------------------------
-- Substrate.WitnessTower.Wedge.PyAstRewritePermRig.PermAlg
--
-- Defines: permAlg
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.WitnessTower.Wedge.PyAstRewritePermRig; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.WitnessTower.Wedge.PyAstRewritePermRig.PermAlg where

open import Substrate.WitnessTower.Enumerate.AllPositions
open import Substrate.WitnessTower.Enumerate.ConcatMapL
open import Substrate.WitnessTower.Enumerate.Factorial
open import Substrate.WitnessTower.Enumerate.InsertAt
open import Substrate.WitnessTower.Enumerate.LenMap
open import Substrate.WitnessTower.Enumerate.LengthAllPositions
open import Substrate.WitnessTower.Enumerate.LengthAppend
open import Substrate.WitnessTower.Enumerate.LengthConcatMapLConst
open import Substrate.WitnessTower.Enumerate.LengthL
open import Substrate.WitnessTower.Enumerate.MapL
open import Substrate.WitnessTower.Enumerate.Perm
open import Substrate.WitnessTower.Enumerate.Perms
open import Substrate.WitnessTower.Enumerate.Perms1Count
open import Substrate.WitnessTower.Enumerate.Perms2Count
open import Substrate.WitnessTower.Enumerate.Perms3Count
open import Substrate.WitnessTower.Enumerate.Perms4Count
open import Substrate.WitnessTower.Enumerate.PermsLength
open import Substrate.WitnessTower.Enumerate.Words
open import Substrate.WitnessTower.Enumerate.Words23Count
open import Substrate.WitnessTower.Enumerate.WordsLength
open import Substrate.WitnessTower.FirstAppearance
open import Substrate.WitnessTower.Wedge.OrientationUniversal



------------------------------------------------------------------------
-- 1. THE PERMUTATION ALGEBRA: base = the empty perm, step = insert-at. Its fold IS
--    `decode` — the LehmerAlgebra underlying the permutation-carrier RigAlgebra.
------------------------------------------------------------------------
permAlg : LehmerAlgebra Perm
permAlg = record { base = id-perm 0 ; step = λ x p → insert-at p x }
