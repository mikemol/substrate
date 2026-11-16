------------------------------------------------------------------------
-- Substrate.WitnessTower.CodewordCountTies.ReservedCount8
--
-- Defines: reserved-count-8
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.WitnessTower.CodewordCountTies; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.WitnessTower.CodewordCountTies.ReservedCount8 where

open import Substrate.Foundation.Nat.Nat
open import Substrate.Foundation.Nat.Pow
open import Substrate.Foundation.Bool.Bool
open import Substrate.Foundation.Vec
open import Substrate.Cocycles.V4Signature.Codeword.Subtypes
open import Substrate.WitnessTower.VecBoolCardinality
open import Substrate.WitnessTower.Enumerate
open import Substrate.Foundation.Eq
open import Substrate.Foundation.Eq.Trans
open import Substrate.Foundation.Eq.Cong2
open import Substrate.Foundation.Negation.Dec
open import Substrate.Foundation.Hedberg.DecidableUIP
open import Substrate.Foundation.Nat.Plus
open import Substrate.WitnessTower.CodewordCountTies.Vec3Tores



-- |Reserved| = 8 : the enumeration of Reserved (as the image of allVB 3 under
-- vec3→res) has length card-VecBool 3 = 8. The count of Reserved codewords is 8.
reserved-count-8 : lengthL (mapL vec3→res (allVB 3)) ≡ 8
reserved-count-8 = trans (length-map vec3→res (allVB 3)) card-reserved-core
  where open import Substrate.WitnessTower.VecBoolCardinality using (length-map)
