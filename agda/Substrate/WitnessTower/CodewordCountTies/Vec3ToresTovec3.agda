------------------------------------------------------------------------
-- Substrate.WitnessTower.CodewordCountTies.Vec3ToresTovec3
--
-- Defines: vec3→res→vec3
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.WitnessTower.CodewordCountTies; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.WitnessTower.CodewordCountTies.Vec3ToresTovec3 where

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
open import Substrate.WitnessTower.CodewordCountTies.ResTovec3
open import Substrate.WitnessTower.CodewordCountTies.Vec3Tores



vec3→res→vec3 : (v : Vec Bool 3) → res→vec3 (vec3→res v) ≡ v
vec3→res→vec3 (b0 ∷ b1 ∷ b2 ∷ []) = refl
