------------------------------------------------------------------------
-- Substrate.Cocycles.V4Signature.Codeword.ReservedToBivectorAffine.Shift
--
-- shift : V₄ → Bivector. The 4 translation bivectors forming the V₄
-- subgroup of (Bivector, +ⱽ): 𝟎ⱽ, sd-pair-01-23, sd-pair-02-13, sum.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Cocycles.V4Signature.Codeword.ReservedToBivectorAffine.Shift where

open import Substrate.Foundation.Bool using (false; true)
open import Substrate.Foundation.Product using (_,_)
open import Substrate.Algebra.F2.HodgeDim4.Bivector using (Bivector)
open import Substrate.Algebra.F2.Vector using (𝟎ⱽ; _+ⱽ_)
open import Substrate.Algebra.F2.HodgeDim4.SelfDual
  using (sd-pair-01-23; sd-pair-02-13)
open import Substrate.Cocycles.V4Signature.Codeword.ReservedToBivectorAffine.V4
  using (V₄)

shift : V₄ → Bivector
shift (false , false) = 𝟎ⱽ
shift (true  , false) = sd-pair-01-23
shift (false , true ) = sd-pair-02-13
shift (true  , true ) = sd-pair-01-23 +ⱽ sd-pair-02-13
