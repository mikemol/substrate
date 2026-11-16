------------------------------------------------------------------------
-- XOR cancels on the left.
-- Context: Substrate/Algebra/CayleyDickson/Curve/README.md
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.CayleyDickson.Curve.XorCancelL where

open import Substrate.Foundation.Bool.Bool
open import Substrate.Foundation.Bool.Xor
open import Substrate.Foundation.Bool.Properties.XorAssoc
open import Substrate.Foundation.Bool.Properties.XorIdentityL
open import Substrate.Foundation.Bool.Properties.XorSame
open import Substrate.Foundation.Eq
open import Substrate.Foundation.Eq.Cong
open import Substrate.Foundation.Eq.Sym
open import Substrate.Foundation.Eq.Trans

xor-cancelˡ : (a b : Bool) → a xor (a xor b) ≡ b
xor-cancelˡ a b =
  trans (sym (xor-assoc a a b)) (trans (cong (_xor b) (xor-same a)) (xor-identityˡ b))
