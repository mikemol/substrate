------------------------------------------------------------------------
-- Substrate.Cocycles.V4Signature.Codeword.ReservedToBivectorAffine.BaseBivector
--
-- The sign-dependent offset: base-bivector false = 𝟎ⱽ,
-- base-bivector true = sd-pair-03-12. Plus the self-dual witness.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Cocycles.V4Signature.Codeword.ReservedToBivectorAffine.BaseBivector where

open import Substrate.Foundation.Bool using (Bool; false; true)
open import Substrate.Algebra.F2.HodgeDim4.Bivector using (Bivector)
open import Substrate.Algebra.F2.Vector using (𝟎ⱽ)
open import Substrate.Algebra.F2.HodgeDim4.SelfDual
  using (SelfDual-Pred; sd-zero; sd-pair-03-12; sd-pair-03-12-self-dual)

base-bivector : Bool → Bivector
base-bivector false = 𝟎ⱽ
base-bivector true  = sd-pair-03-12

base-bivector-sd : (b : Bool) → SelfDual-Pred (base-bivector b)
base-bivector-sd false = sd-zero
base-bivector-sd true  = sd-pair-03-12-self-dual
