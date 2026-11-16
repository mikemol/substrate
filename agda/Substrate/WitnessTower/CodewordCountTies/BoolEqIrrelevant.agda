------------------------------------------------------------------------
-- Substrate.WitnessTower.CodewordCountTies.BoolEqIrrelevant
--
-- Defines: bool-≡-irrelevant
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.WitnessTower.CodewordCountTies; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.WitnessTower.CodewordCountTies.BoolEqIrrelevant where

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
open import Substrate.WitnessTower.CodewordCountTies.DecB



-- ≡-on-Bool is proof-irrelevant (Hedberg on decidable Bool equality).
bool-≡-irrelevant : {x y : Bool} (p q : x ≡ y) → p ≡ q
bool-≡-irrelevant = Decidable⇒UIP _≟B_
