------------------------------------------------------------------------
-- Substrate.WitnessTower.CodewordCountTies.IsReservedIrrelevant
--
-- Defines: isReserved-irrelevant
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.WitnessTower.CodewordCountTies; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.WitnessTower.CodewordCountTies.IsReservedIrrelevant where

open import Substrate.Foundation.Nat.Nat
open import Substrate.Foundation.Nat.Pow
open import Substrate.Foundation.Bool.Bool
open import Substrate.Foundation.Vec
open import Substrate.Cocycles.V4Signature.Codeword.Type
open import Substrate.Cocycles.V4Signature.Codeword.IsReserved
open import Substrate.Cocycles.V4Signature.Codeword.Subtypes
open import Substrate.Foundation.Eq
open import Substrate.Foundation.Eq.Trans
open import Substrate.Foundation.Eq.Cong2
open import Substrate.Foundation.Negation.Dec
open import Substrate.Foundation.Hedberg.DecidableUIP
open import Substrate.Foundation.Nat.Plus
open import Substrate.WitnessTower.CodewordCountTies.BoolEqIrrelevant
open import Substrate.Foundation.Product



-- hence IsReserved is proof-irrelevant (a product of two irrelevant ≡'s).
isReserved-irrelevant : (cw : Codeword) (p q : IsReserved cw) → p ≡ q
isReserved-irrelevant cw (p3 , p4) (q3 , q4) =
  cong₂ _,_ (bool-≡-irrelevant p3 q3) (bool-≡-irrelevant p4 q4)
  where open import Substrate.Foundation.Eq using (cong₂)
