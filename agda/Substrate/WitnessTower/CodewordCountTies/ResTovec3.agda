------------------------------------------------------------------------
-- Substrate.WitnessTower.CodewordCountTies.ResTovec3
--
-- Defines: res→vec3
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.WitnessTower.CodewordCountTies; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.WitnessTower.CodewordCountTies.ResTovec3 where

open import Substrate.Foundation.Nat.Nat
open import Substrate.Foundation.Nat.Pow
open import Substrate.Foundation.Bool.Bool
open import Substrate.Foundation.Vec
open import Substrate.Cocycles.V4Signature.Codeword.IsReserved
open import Substrate.Cocycles.V4Signature.Codeword.Subtypes
open import Substrate.Foundation.Eq
open import Substrate.Foundation.Eq.Trans
open import Substrate.Foundation.Eq.Cong2
open import Substrate.Foundation.Negation.Dec
open import Substrate.Foundation.Hedberg.DecidableUIP
open import Substrate.Foundation.Nat.Plus
open import Substrate.Foundation.Product



-- the bijection: a Reserved codeword's three free bits (0,1,2) ↔ Vec Bool 3;
-- bits 3,4 are pinned false by IsReserved.
res→vec3 : Reserved → Vec Bool 3
res→vec3 ((b0 , b1 , b2 , b3 , b4) , _) = b0 ∷ b1 ∷ b2 ∷ []
