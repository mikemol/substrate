------------------------------------------------------------------------
-- Substrate.Cocycles.V4Signature.Codeword.ReservedToBivectorAffine.ShiftSelfDual
--
-- shift-sd : (v : V₄) → SelfDual-Pred (shift v). Each of the 4
-- translation bivectors is self-dual.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Cocycles.V4Signature.Codeword.ReservedToBivectorAffine.ShiftSelfDual where

open import Substrate.Foundation.Bool using (false; true)
open import Substrate.Foundation.Product using (_,_)
open import Substrate.Algebra.F2.HodgeDim4.SelfDual
  using (SelfDual-Pred; sd-zero; sd-pair-01-23; sd-pair-02-13;
         sd-pair-01-23-self-dual; sd-pair-02-13-self-dual;
         sd-closed-+ⱽ)
open import Substrate.Cocycles.V4Signature.Codeword.ReservedToBivectorAffine.V4
  using (V₄)
open import Substrate.Cocycles.V4Signature.Codeword.ReservedToBivectorAffine.Shift
  using (shift)

shift-sd : (v : V₄) → SelfDual-Pred (shift v)
shift-sd (false , false) = sd-zero
shift-sd (true  , false) = sd-pair-01-23-self-dual
shift-sd (false , true ) = sd-pair-02-13-self-dual
shift-sd (true  , true ) =
  sd-closed-+ⱽ sd-pair-01-23 sd-pair-02-13
    sd-pair-01-23-self-dual sd-pair-02-13-self-dual
