------------------------------------------------------------------------
-- Substrate.WitnessTower.LehmerPath.EncodeDecode2
--
-- Defines: encode-decode
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.WitnessTower.LehmerPath; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.WitnessTower.LehmerPath.EncodeDecode2 where

open import Substrate.Foundation.Nat.Nat
open import Substrate.Foundation.Fin.Fin
open import Substrate.WitnessTower.Enumerate.InsertAt
open import Substrate.WitnessTower.Enumerate.Perm
open import Substrate.WitnessTower.IsPermutation
open import Substrate.WitnessTower.Decompose
open import Substrate.WitnessTower.LehmerPath.LehmerPath
open import Substrate.WitnessTower.LehmerPath.Decode
open import Substrate.WitnessTower.LehmerPath.DecodeIsPerm
open import Substrate.WitnessTower.LehmerPath.Encode
open import Substrate.WitnessTower.LehmerPath.EncodeDecode
open import Substrate.Foundation.Eq



encode-decode : ∀ {n} (l : LehmerPath n) →
                encode (decode l) (decode-is-perm l) ≡ l
encode-decode l = encode-decode′ l (decode-is-perm l)
