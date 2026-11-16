------------------------------------------------------------------------
-- Substrate.WitnessTower.CodewordCountTies.Blk
--
-- Defines: blk
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.WitnessTower.CodewordCountTies; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.WitnessTower.CodewordCountTies.Blk where

open import Substrate.Foundation.Nat.Nat
open import Substrate.Foundation.Nat.Pow
open import Substrate.Foundation.Bool.Bool
open import Substrate.Foundation.Vec
open import Substrate.Foundation.Product
open import Substrate.Cocycles.V4Signature.Codeword.Type
open import Substrate.Cocycles.V4Signature.Codeword.Subtypes
open import Substrate.WitnessTower.VecBoolCardinality
open import Substrate.WitnessTower.Enumerate
open import Substrate.Foundation.Eq
open import Substrate.Foundation.Eq.Trans
open import Substrate.Foundation.Eq.Cong2
open import Substrate.Foundation.Negation.Dec
open import Substrate.Foundation.Hedberg.DecidableUIP
open import Substrate.Foundation.Nat.Plus
open import Substrate.WitnessTower.CodewordCountTies.MkLive



blk : (t : Bool × Bool) → lengthL (mapL (mkLive t) (allVB 3)) ≡ 8
blk t = trans (length-map (mkLive t) (allVB 3)) card-reserved-core
