------------------------------------------------------------------------
-- Substrate.WitnessTower.LehmerPath.Encode
--
-- Defines: encode
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.WitnessTower.LehmerPath; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.WitnessTower.LehmerPath.Encode where

open import Substrate.Foundation.Nat.Nat
open import Substrate.Foundation.Fin.Fin
open import Substrate.WitnessTower.Enumerate.Perm
open import Substrate.WitnessTower.IsPermutation
open import Substrate.WitnessTower.Decompose
open import Substrate.WitnessTower.LehmerPath.LehmerPath



------------------------------------------------------------------------
-- 3. encode = the inverse walk: peel the top element off with `decompose`
--    (its position is the rung's choice), recurse on the smaller permutation.
------------------------------------------------------------------------

encode : ∀ {n} (σ : Perm n) → IsPerm σ → LehmerPath n
encode {zero}  σ perm = start
encode {suc n} σ perm =
  encode (decomp-tail σ perm) (decomp-tail-perm σ perm) ◂ decomp-head σ
