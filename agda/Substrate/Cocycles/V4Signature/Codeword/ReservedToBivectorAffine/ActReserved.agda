------------------------------------------------------------------------
-- Substrate.Cocycles.V4Signature.Codeword.ReservedToBivectorAffine.ActReserved
--
-- v4-act-reserved : V₄ → Reserved → Reserved.
-- V₄ acts on Reserved by axis-addition (regular representation on
-- the axis bits b₀, b₁); the sign b₂ and reserved tail bits are
-- untouched.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Cocycles.V4Signature.Codeword.ReservedToBivectorAffine.ActReserved where

open import Substrate.Foundation.Bool using (Bool; false; _xor_)
open import Substrate.Foundation.Product using (_,_)
open import Substrate.Foundation.Eq using (refl)
open import Substrate.Cocycles.V4Signature.Codeword.Subtypes using (Reserved)
open import Substrate.Cocycles.V4Signature.Codeword.ReservedToBivectorAffine.V4
  using (V₄)

v4-act-reserved : V₄ → Reserved → Reserved
v4-act-reserved (a , b) ((b₀ , b₁ , b₂ , .false , .false) , refl , refl) =
  ((a xor b₀ , b xor b₁ , b₂ , false , false) , refl , refl)
