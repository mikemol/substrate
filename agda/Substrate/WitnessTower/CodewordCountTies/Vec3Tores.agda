------------------------------------------------------------------------
-- Substrate.WitnessTower.CodewordCountTies.Vec3Tores
--
-- Defines: vec3→res
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.WitnessTower.CodewordCountTies; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.WitnessTower.CodewordCountTies.Vec3Tores where

open import Substrate.Foundation.Nat.Nat
open import Substrate.Foundation.Nat.Pow
open import Substrate.Foundation.Bool.Bool
open import Substrate.Foundation.Vec
open import Substrate.Cocycles.V4Signature.Codeword.Subtypes
open import Substrate.Foundation.Eq
open import Substrate.Foundation.Eq.Trans
open import Substrate.Foundation.Eq.Cong2
open import Substrate.Foundation.Negation.Dec
open import Substrate.Foundation.Hedberg.DecidableUIP
open import Substrate.Foundation.Nat.Plus
open import Substrate.Foundation.Product



vec3→res : Vec Bool 3 → Reserved
vec3→res (b0 ∷ b1 ∷ b2 ∷ []) = (b0 , b1 , b2 , false , false) , (refl , refl)
