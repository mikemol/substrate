------------------------------------------------------------------------
-- Substrate.Cocycles.V4Signature.Codeword.ReservedToBivectorAffine.XorSelf
--
-- xor-self : (a : Bool) → a xor a ≡ false. Used in shift-hom's
-- diagonal cases (where the same V₄ element appears on both sides
-- of +V₄ and cancels via self-inverse).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Cocycles.V4Signature.Codeword.ReservedToBivectorAffine.XorSelf where

open import Substrate.Foundation.Bool.Bool
open import Substrate.Foundation.Bool.Xor
open import Substrate.Foundation.Eq

xor-self : (a : Bool) → (a xor a) ≡ false
xor-self false = refl
xor-self true  = refl
