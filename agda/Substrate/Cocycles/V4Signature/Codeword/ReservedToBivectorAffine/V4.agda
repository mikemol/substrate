------------------------------------------------------------------------
-- Substrate.Cocycles.V4Signature.Codeword.ReservedToBivectorAffine.V4
--
-- V₄ as F₂² (additive group). The V₄ subgroup of Aff(3, F₂) used by
-- the sacrifice-ladder rung's translation action.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Cocycles.V4Signature.Codeword.ReservedToBivectorAffine.V4 where

open import Substrate.Foundation.Bool using (Bool; _xor_)
open import Substrate.Foundation.Product using (_×_; _,_)

V₄ : Set
V₄ = Bool × Bool

_+V₄_ : V₄ → V₄ → V₄
(a , b) +V₄ (c , d) = (a xor c) , (b xor d)
