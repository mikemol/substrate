------------------------------------------------------------------------
-- Substrate.WitnessTower.CodewordCountTies.DecB
--
-- Defines: _≟B_
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.WitnessTower.CodewordCountTies; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.WitnessTower.CodewordCountTies.DecB where

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



------------------------------------------------------------------------
-- ◆AI-1b''' : |Reserved| = EXACTLY 8 (not merely ≥8 distinct). The remaining
--   leg is that res→vec3 is surjective, i.e. vec3→res (res→vec3 r) ≡ r — which
--   needs the PROOF component of IsReserved to be irrelevant (a Reserved's
--   (bit₃≡false , bit₄≡false) proof is unique). IsReserved is a product of ≡-on-
--   Bool, and Bool has decidable equality, so by Hedberg ≡-on-Bool is a Prop.
------------------------------------------------------------------------


_≟B_ : (x y : Bool) → Dec (x ≡ y)
true  ≟B true  = yes refl
false ≟B false = yes refl
true  ≟B false = no (λ ())
false ≟B true  = no (λ ())
