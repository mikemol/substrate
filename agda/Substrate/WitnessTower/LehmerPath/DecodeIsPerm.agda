------------------------------------------------------------------------
-- Substrate.WitnessTower.LehmerPath.DecodeIsPerm
--
-- Defines: decode-is-perm
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.WitnessTower.LehmerPath; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.WitnessTower.LehmerPath.DecodeIsPerm where

open import Substrate.Foundation.Nat.Nat
open import Substrate.Foundation.Fin.Fin
open import Substrate.WitnessTower.Enumerate.InsertAt
open import Substrate.WitnessTower.Enumerate.Perm
open import Substrate.WitnessTower.IsPermutation
open import Substrate.WitnessTower.LehmerPath.LehmerPath
open import Substrate.WitnessTower.LehmerPath.Decode



decode-is-perm : ∀ {n} (l : LehmerPath n) → IsPerm (decode l)
decode-is-perm start   = IsPerm-[]
decode-is-perm (l ◂ p) = insert-at-preserves p (decode l) (decode-is-perm l)
