------------------------------------------------------------------------
-- Substrate.WitnessTower.CodewordCountTies.ReservedExactly8
--
-- Defines: reserved-exactly-8
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.WitnessTower.CodewordCountTies; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.WitnessTower.CodewordCountTies.ReservedExactly8 where

open import Substrate.Foundation.Nat.Nat
open import Substrate.Foundation.Nat.Pow
open import Substrate.Foundation.Bool.Bool
open import Substrate.Foundation.Vec
open import Substrate.Cocycles.V4Signature.Codeword.IsReserved
open import Substrate.Cocycles.V4Signature.Codeword.Subtypes
open import Substrate.WitnessTower.VecBoolCardinality
open import Substrate.WitnessTower.Enumerate
open import Substrate.Foundation.Eq
open import Substrate.Foundation.Eq.Trans
open import Substrate.Foundation.Eq.Cong2
open import Substrate.Foundation.Negation.Dec
open import Substrate.Foundation.Hedberg.DecidableUIP
open import Substrate.Foundation.Nat.Plus
open import Substrate.WitnessTower.CodewordCountTies.ResTovec3
open import Substrate.WitnessTower.CodewordCountTies.Vec3Tores
open import Substrate.WitnessTower.CodewordCountTies.Vec3ToresTovec3
open import Substrate.WitnessTower.CodewordCountTies.ReservedCount8
open import Substrate.WitnessTower.CodewordCountTies.ResRoundtrip



-- Reserved ≅ Vec Bool 3 is now a full bijection (both roundtrips):
--   vec3→res→vec3 (the free-bits side) and res-roundtrip (the Reserved side).
-- Composing card-VecBool 3 across it: |Reserved| = 8 EXACTLY.
reserved-exactly-8 : lengthL (mapL vec3→res (allVB 3)) ≡ 8
reserved-exactly-8 = reserved-count-8
