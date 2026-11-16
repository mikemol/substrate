------------------------------------------------------------------------
-- Substrate.WitnessTower.CodewordCountTies.LiveCount24
--
-- Defines: live-count-24
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.WitnessTower.CodewordCountTies; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.WitnessTower.CodewordCountTies.LiveCount24 where

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
open import Substrate.Foundation.List
open import Substrate.WitnessTower.CodewordCountTies.MkLive
open import Substrate.WitnessTower.CodewordCountTies.AllLive
open import Substrate.WitnessTower.CodewordCountTies.Blk
open import Substrate.WitnessTower.CodewordCountTies.TailBlock



live-count-24 : lengthL allLive ≡ 24
live-count-24 =
  trans (length-++ (mapL (mkLive (true , false)) (allVB 3)) tail-block)
        (cong₂ _ℕ+_ (blk (true , false))
          (trans (length-++ (mapL (mkLive (false , true)) (allVB 3))
                            (mapL (mkLive (true , true )) (allVB 3)))
                 (cong₂ _ℕ+_ (blk (false , true)) (blk (true , true)))))
