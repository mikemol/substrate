------------------------------------------------------------------------
-- Substrate.WitnessTower.Wedge.PyAstRewritePermRig.FoldPermAlgEqdecode
--
-- Defines: fold-permAlg≡decode
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.WitnessTower.Wedge.PyAstRewritePermRig; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.WitnessTower.Wedge.PyAstRewritePermRig.FoldPermAlgEqdecode where

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
open import Substrate.WitnessTower.LehmerPath.Decode
open import Substrate.WitnessTower.LehmerPath.DecodeEncode
open import Substrate.WitnessTower.LehmerPath.DecodeIsPerm
open import Substrate.WitnessTower.LehmerPath.DecompHeadInsert
open import Substrate.WitnessTower.LehmerPath.DecompTailInsert
open import Substrate.WitnessTower.LehmerPath.Encode
open import Substrate.WitnessTower.LehmerPath.EncodeDecode
open import Substrate.WitnessTower.LehmerPath.EncodeDecode2
open import Substrate.WitnessTower.LehmerPath.LehmerPath
open import Substrate.WitnessTower.Wedge.OrientationUniversal
open import Substrate.WitnessTower.Wedge.PyAstRewritePermRig.PermAlg
open import Substrate.Foundation.Eq
open import Substrate.Foundation.Eq.Cong



-- fold permAlg ≡ decode: the "derived from a LehmerAlgebra, shown equivalent" — the
-- permutation reading is exactly the tower's decode.
fold-permAlg≡decode : ∀ {n} (l : LehmerPath n) → fold permAlg l ≡ decode l
fold-permAlg≡decode start   = refl
fold-permAlg≡decode (l ◂ p) = cong (insert-at p) (fold-permAlg≡decode l)
